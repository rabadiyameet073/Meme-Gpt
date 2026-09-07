// MemeGPT Progress Tracker — VS Code Extension
// Shows contextual completion/quality percentages on all files in the explorer

const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { analyzeFile, computeFolderPercentage, getDomainLabel } = require('./analyzer');
const { parseTestResults, getTestFileResults } = require('./test-parser');

// ─── Color Thresholds ───────────────────────────────────────────────────────
const COLOR_EXCELLENT = 'charts.green';       // 90-100%
const COLOR_GOOD = 'charts.yellow';           // 70-89%
const COLOR_NEEDS_WORK = 'charts.orange';     // 50-69%
const COLOR_CRITICAL = 'errorForeground';     // 0-49%

function getColorForPercentage(pct) {
    if (pct >= 90) return COLOR_EXCELLENT;
    if (pct >= 70) return COLOR_GOOD;
    if (pct >= 50) return COLOR_NEEDS_WORK;
    return COLOR_CRITICAL;
}

function getBadgeForPercentage(pct) {
    pct = Math.round(pct);
    if (pct === 100) return '✓';
    if (pct >= 10) return String(pct);
    return String(pct);
}

// ─── FileDecorationProvider ─────────────────────────────────────────────────
class ProgressDecorationProvider {
    constructor(workspaceRoot) {
        this._onDidChangeFileDecorations = new vscode.EventEmitter();
        this.onDidChangeFileDecorations = this._onDidChangeFileDecorations.event;
        this._cache = new Map();          // fsPath → { percentage, tooltip, domain }
        this._folderCache = new Map();    // fsPath → { percentage, tooltip }
        this._workspaceRoot = workspaceRoot;
        this._testResults = null;
        this._cacheFilePath = path.join(workspaceRoot, '.vscode', 'progress-cache.json');
        this._testResultsPath = path.join(workspaceRoot, '.vscode', 'test-results.json');

        // Directories / files to skip
        this._skipPatterns = [
            'node_modules', '__pycache__', '.git', '.pytest_cache',
            'dist', 'build', '.vscode', 'model_cache', '.openclaude',
            'logs', '.coverage', '.env', 'memegpt.db', 'package-lock.json',
            'tsconfig.tsbuildinfo', '.gitignore'
        ];
    }

    _shouldSkip(filePath) {
        const rel = path.relative(this._workspaceRoot, filePath);
        const parts = rel.split(path.sep);
        return parts.some(p => this._skipPatterns.includes(p));
    }

    // ── Initial Workspace Scan ──────────────────────────────────────────────
    async analyzeWorkspace() {
        const startTime = Date.now();
        console.log('[MemeGPT Progress] Starting workspace analysis...');

        // Load test results if available
        this._testResults = parseTestResults(this._testResultsPath, this._workspaceRoot);

        // Scan all files recursively
        await this._scanDirectory(this._workspaceRoot);

        // Compute folder percentages bottom-up
        this._computeFolderPercentages(this._workspaceRoot);

        // Save cache
        this._saveCache();

        const elapsed = Date.now() - startTime;
        console.log(`[MemeGPT Progress] Analysis complete in ${elapsed}ms. ${this._cache.size} files, ${this._folderCache.size} folders analyzed.`);

        // Fire change event to refresh all decorations
        this._onDidChangeFileDecorations.fire(undefined);
    }

    async _scanDirectory(dirPath) {
        let entries;
        try {
            entries = fs.readdirSync(dirPath, { withFileTypes: true });
        } catch {
            return;
        }

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);

            if (this._shouldSkip(fullPath)) continue;

            if (entry.isDirectory()) {
                await this._scanDirectory(fullPath);
            } else if (entry.isFile()) {
                await this._analyzeAndCacheFile(fullPath);
            }
        }
    }

    async _analyzeAndCacheFile(filePath) {
        try {
            const relativePath = path.relative(this._workspaceRoot, filePath);
            const testResults = getTestFileResults(this._testResults, relativePath);
            const result = analyzeFile(filePath, this._workspaceRoot, testResults);

            if (result) {
                this._cache.set(filePath, result);
            }
        } catch (err) {
            console.warn(`[MemeGPT Progress] Error analyzing ${filePath}: ${err.message}`);
        }
    }

    _computeFolderPercentages(dirPath) {
        let entries;
        try {
            entries = fs.readdirSync(dirPath, { withFileTypes: true });
        } catch {
            return null;
        }

        const childPercentages = [];

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);
            if (this._shouldSkip(fullPath)) continue;

            if (entry.isDirectory()) {
                const subResult = this._computeFolderPercentages(fullPath);
                if (subResult !== null) {
                    childPercentages.push(subResult);
                }
            } else if (entry.isFile()) {
                const fileResult = this._cache.get(fullPath);
                if (fileResult) {
                    childPercentages.push(fileResult.percentage);
                }
            }
        }

        if (childPercentages.length === 0) return null;

        const avg = Math.round(childPercentages.reduce((a, b) => a + b, 0) / childPercentages.length);
        const folderName = path.basename(dirPath);
        const domain = getDomainLabel(dirPath, this._workspaceRoot, true);

        this._folderCache.set(dirPath, {
            percentage: avg,
            tooltip: `📁 ${folderName} — ${domain}\n${avg}% average across ${childPercentages.length} items\nRange: ${Math.min(...childPercentages)}% – ${Math.max(...childPercentages)}%`,
            domain: domain
        });

        return avg;
    }

    // ── Provide Decorations ─────────────────────────────────────────────────
    provideFileDecoration(uri) {
        if (uri.scheme !== 'file') return undefined;

        const filePath = uri.fsPath;
        if (this._shouldSkip(filePath)) return undefined;

        // Check file cache
        const fileResult = this._cache.get(filePath);
        if (fileResult) {
            return new vscode.FileDecoration(
                getBadgeForPercentage(fileResult.percentage),
                `${fileResult.percentage}% — ${fileResult.domain}\n${fileResult.tooltip}`,
                new vscode.ThemeColor(getColorForPercentage(fileResult.percentage))
            );
        }

        // Check folder cache
        const folderResult = this._folderCache.get(filePath);
        if (folderResult) {
            return new vscode.FileDecoration(
                getBadgeForPercentage(folderResult.percentage),
                folderResult.tooltip,
                new vscode.ThemeColor(getColorForPercentage(folderResult.percentage))
            );
        }

        return undefined;
    }

    // ── Refresh Single File ─────────────────────────────────────────────────
    async refreshFile(uri) {
        const filePath = uri.fsPath;
        if (this._shouldSkip(filePath)) return;

        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            await this._analyzeAndCacheFile(filePath);
        }

        // Recompute folder percentages up the chain
        let dir = path.dirname(filePath);
        while (dir !== this._workspaceRoot && dir.startsWith(this._workspaceRoot)) {
            this._computeFolderPercentages(dir);
            dir = path.dirname(dir);
        }
        this._computeFolderPercentages(this._workspaceRoot);

        this._onDidChangeFileDecorations.fire(uri);
    }

    // ── Cache Persistence ───────────────────────────────────────────────────
    _saveCache() {
        try {
            const data = {};
            for (const [key, val] of this._cache) {
                data[path.relative(this._workspaceRoot, key)] = val;
            }
            const folderData = {};
            for (const [key, val] of this._folderCache) {
                folderData[path.relative(this._workspaceRoot, key)] = val;
            }
            const cacheContent = JSON.stringify({ files: data, folders: folderData, timestamp: Date.now() }, null, 2);
            fs.mkdirSync(path.dirname(this._cacheFilePath), { recursive: true });
            fs.writeFileSync(this._cacheFilePath, cacheContent, 'utf8');
        } catch (err) {
            console.warn('[MemeGPT Progress] Failed to save cache:', err.message);
        }
    }

    _loadCache() {
        try {
            if (fs.existsSync(this._cacheFilePath)) {
                const raw = fs.readFileSync(this._cacheFilePath, 'utf8');
                const data = JSON.parse(raw);

                if (data.files) {
                    for (const [rel, val] of Object.entries(data.files)) {
                        this._cache.set(path.join(this._workspaceRoot, rel), val);
                    }
                }
                if (data.folders) {
                    for (const [rel, val] of Object.entries(data.folders)) {
                        this._folderCache.set(path.join(this._workspaceRoot, rel), val);
                    }
                }
                return true;
            }
        } catch {
            // ignore
        }
        return false;
    }
}

// ─── Extension Activation ───────────────────────────────────────────────────
function activate(context) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        console.log('[MemeGPT Progress] No workspace folder found, skipping.');
        return;
    }

    const config = vscode.workspace.getConfiguration('memegpt-progress');
    if (!config.get('enabled', true)) {
        console.log('[MemeGPT Progress] Extension disabled by setting.');
        return;
    }

    const workspaceRoot = workspaceFolder.uri.fsPath;
    const provider = new ProgressDecorationProvider(workspaceRoot);

    // Register the FileDecorationProvider
    context.subscriptions.push(
        vscode.window.registerFileDecorationProvider(provider)
    );

    // Load cached results first for instant display
    const hasCache = provider._loadCache();
    if (hasCache) {
        provider._onDidChangeFileDecorations.fire(undefined);
        console.log('[MemeGPT Progress] Loaded cached percentages');
    }

    // Full analysis in background
    provider.analyzeWorkspace().catch(err => {
        console.error('[MemeGPT Progress] Workspace analysis failed:', err);
    });

    // Watch for file changes
    if (config.get('autoRefresh', true)) {
        const watcher = vscode.workspace.createFileSystemWatcher('**/*', false, false, false);

        watcher.onDidChange(uri => {
            if (config.get('refreshOnSave', true)) {
                provider.refreshFile(uri);
            }
        });
        watcher.onDidCreate(uri => provider.refreshFile(uri));
        watcher.onDidDelete(uri => {
            provider._cache.delete(uri.fsPath);
            provider._folderCache.delete(uri.fsPath);
            provider._onDidChangeFileDecorations.fire(uri);
        });

        context.subscriptions.push(watcher);
    }

    // Also refresh on document save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(doc => {
            if (config.get('refreshOnSave', true)) {
                provider.refreshFile(doc.uri);
            }
        })
    );

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('memegpt-progress.refresh', async () => {
            vscode.window.withProgress(
                { location: vscode.ProgressLocation.Notification, title: 'MemeGPT: Refreshing progress...' },
                async () => {
                    provider._cache.clear();
                    provider._folderCache.clear();
                    await provider.analyzeWorkspace();
                    vscode.window.showInformationMessage(`MemeGPT Progress: Analyzed ${provider._cache.size} files`);
                }
            );
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('memegpt-progress.runTests', async () => {
            const terminal = vscode.window.createTerminal('MemeGPT Tests');
            terminal.show();
            terminal.sendText(`cd "${path.join(workspaceRoot, 'backend')}" && python -m pytest tests/ -v --tb=short -q 2>&1 | Tee-Object "${path.join(workspaceRoot, '.vscode', 'last-test-output.txt')}"`);
            vscode.window.showInformationMessage('MemeGPT: Running tests... Refresh progress after completion.');
        })
    );

    console.log('[MemeGPT Progress] Extension activated for:', workspaceRoot);
}

function deactivate() {
    console.log('[MemeGPT Progress] Extension deactivated');
}

module.exports = { activate, deactivate };
