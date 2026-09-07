// MemeGPT Progress Tracker — Test Results Parser
// Parses pytest and vitest output for per-file test pass/fail rates

const fs = require('fs');
const path = require('path');

/**
 * Parses stored test results from the test results cache file.
 * Also attempts to parse the last raw pytest output if cache is stale.
 * 
 * @param {string} testResultsPath - Path to .vscode/test-results.json
 * @param {string} workspaceRoot - Root of the workspace
 * @returns {object|null} Map of relative file paths to { passed, failed, failures }
 */
function parseTestResults(testResultsPath, workspaceRoot) {
    let results = null;

    // Try loading cached results first
    try {
        if (fs.existsSync(testResultsPath)) {
            const raw = fs.readFileSync(testResultsPath, 'utf8');
            results = JSON.parse(raw);
            console.log('[MemeGPT Progress] Loaded cached test results');
        }
    } catch {
        // ignore
    }

    // Try parsing raw pytest output
    const rawOutputPath = path.join(workspaceRoot, '.vscode', 'last-test-output.txt');
    try {
        if (fs.existsSync(rawOutputPath)) {
            const rawOutput = fs.readFileSync(rawOutputPath, 'utf8');
            const parsed = parsePytestOutput(rawOutput, workspaceRoot);
            if (parsed && Object.keys(parsed).length > 0) {
                results = mergeResults(results, parsed);
                // Save merged results
                try {
                    fs.writeFileSync(testResultsPath, JSON.stringify(results, null, 2), 'utf8');
                } catch { /* ignore */ }
            }
        }
    } catch {
        // ignore
    }

    // Try parsing .pytest_cache for last result summary
    const pytestCachePath = path.join(workspaceRoot, 'backend', '.pytest_cache', 'v', 'cache', 'lastfailed');
    try {
        if (fs.existsSync(pytestCachePath)) {
            const cacheContent = fs.readFileSync(pytestCachePath, 'utf8');
            const lastFailed = JSON.parse(cacheContent);
            if (lastFailed && typeof lastFailed === 'object') {
                if (!results) results = {};
                for (const testId of Object.keys(lastFailed)) {
                    // testId format: "tests/test_file.py::test_func_name"
                    const parts = testId.split('::');
                    if (parts.length >= 2) {
                        const filePath = parts[0].replace(/\//g, path.sep);
                        const relPath = filePath.startsWith('tests') ? path.join('backend', filePath) : filePath;

                        if (!results[relPath]) {
                            results[relPath] = { passed: 0, failed: 0, failures: [] };
                        }
                        results[relPath].failed++;
                        results[relPath].failures.push(parts[1]);
                    }
                }
            }
        }
    } catch {
        // ignore
    }

    // Also scan test files to count total test functions per file
    if (results) {
        const testsDir = path.join(workspaceRoot, 'backend', 'tests');
        try {
            if (fs.existsSync(testsDir)) {
                const testFiles = fs.readdirSync(testsDir).filter(f => f.startsWith('test_') && f.endsWith('.py'));
                for (const file of testFiles) {
                    const relPath = path.join('backend', 'tests', file);
                    const fullPath = path.join(testsDir, file);
                    try {
                        const content = fs.readFileSync(fullPath, 'utf8');
                        const testFuncCount = (content.match(/^\s*def\s+test_/gm) || []).length;

                        if (!results[relPath]) {
                            // No failures recorded = all passed
                            results[relPath] = { passed: testFuncCount, failed: 0, failures: [] };
                        } else {
                            // Calculate passed = total - failed
                            const failed = results[relPath].failed || 0;
                            results[relPath].passed = Math.max(0, testFuncCount - failed);
                            results[relPath].total = testFuncCount;
                        }
                    } catch { /* ignore */ }
                }
            }
        } catch { /* ignore */ }
    }

    return results;
}

/**
 * Parse raw pytest verbose output to extract per-file results
 * Expects output from: pytest tests/ -v --tb=no -q
 */
function parsePytestOutput(output, workspaceRoot) {
    const results = {};
    const lines = output.split('\n');

    for (const line of lines) {
        // Match lines like: FAILED tests\test_file.py::test_func_name - ...
        const failMatch = line.match(/^FAILED\s+([\w\\\/]+\.py)::(\w+)/);
        if (failMatch) {
            const filePath = failMatch[1].replace(/\//g, path.sep);
            const testName = failMatch[2];
            const relPath = filePath.startsWith('tests') ? path.join('backend', filePath) : filePath;

            if (!results[relPath]) {
                results[relPath] = { passed: 0, failed: 0, failures: [] };
            }
            results[relPath].failed++;
            results[relPath].failures.push(testName);
        }

        // Match lines like: tests/test_file.py::test_func PASSED
        const passMatch = line.match(/([\w\\\/]+\.py)::(\w+)\s+PASSED/);
        if (passMatch) {
            const filePath = passMatch[1].replace(/\//g, path.sep);
            const relPath = filePath.startsWith('tests') ? path.join('backend', filePath) : filePath;

            if (!results[relPath]) {
                results[relPath] = { passed: 0, failed: 0, failures: [] };
            }
            results[relPath].passed++;
        }
    }

    // Parse summary line: "X failed, Y passed, Z warnings in Ns"
    const summaryMatch = output.match(/(\d+)\s+failed.*?(\d+)\s+passed/);
    if (summaryMatch) {
        console.log(`[MemeGPT Progress] Test summary: ${summaryMatch[1]} failed, ${summaryMatch[2]} passed`);
    }

    return results;
}

/**
 * Merge two result sets, preferring newer data
 */
function mergeResults(existing, newer) {
    if (!existing) return newer;
    if (!newer) return existing;

    const merged = { ...existing };
    for (const [key, val] of Object.entries(newer)) {
        merged[key] = val;
    }
    return merged;
}

/**
 * Get test results for a specific file
 * 
 * @param {object|null} allResults - All test results
 * @param {string} relativePath - Relative path of the test file
 * @returns {object|null} { passed, failed, failures } or null
 */
function getTestFileResults(allResults, relativePath) {
    if (!allResults) return null;

    // Normalize path separators
    const normalized = relativePath.replace(/\//g, path.sep);

    // Direct match
    if (allResults[normalized]) {
        return allResults[normalized];
    }

    // Try with/without 'backend/' prefix
    const withBackend = path.join('backend', normalized);
    if (allResults[withBackend]) {
        return allResults[withBackend];
    }

    const withoutBackend = normalized.replace(/^backend[\\\/]/, '');
    if (allResults[withoutBackend]) {
        return allResults[withoutBackend];
    }

    return null;
}

module.exports = { parseTestResults, getTestFileResults, parsePytestOutput };
