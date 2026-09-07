// MemeGPT Progress Tracker — File Analyzer
// Domain-specific analysis engine that calculates completion/quality percentages

const path = require('path');
const fs = require('fs');

// ─── Domain Detection ───────────────────────────────────────────────────────

function detectDomain(filePath, workspaceRoot) {
    const rel = path.relative(workspaceRoot, filePath).replace(/\\/g, '/');
    const ext = path.extname(filePath).toLowerCase();
    const basename = path.basename(filePath).toLowerCase();

    // Test files
    if (basename.startsWith('test_') && ext === '.py') return 'python-test';
    if (basename.endsWith('.test.ts') || basename.endsWith('.test.tsx')) return 'frontend-test';
    if (basename === 'conftest.py') return 'test-config';

    // Backend domains
    if (rel.startsWith('backend/app/api/')) return 'api-route';
    if (rel.startsWith('backend/app/services/')) return 'service';
    if (rel.startsWith('backend/app/models/')) return 'model';
    if (rel.startsWith('backend/app/core/')) return 'core';
    if (rel.startsWith('backend/app/repositories/')) return 'repository';
    if (rel.startsWith('backend/app/jobs/')) return 'background-job';
    if (rel.startsWith('backend/scripts/') || rel.startsWith('scripts/')) return 'script';
    if (rel.startsWith('backend/data/') || rel.startsWith('data/')) return 'data';
    if (basename === 'database.py') return 'database';
    if (basename === 'config.py' && rel.includes('backend')) return 'config';
    if (basename === 'main.py') return 'main-entry';
    if (basename === 'meme_matcher.py') return 'ai-matcher';
    if (basename === 'rule_engine.py') return 'ai-engine';
    if (basename === 'semantic_search.py') return 'ai-search';

    // Frontend domains
    if (rel.startsWith('frontend/src/components/') && (ext === '.tsx' || ext === '.ts')) return 'component';
    if (rel.startsWith('frontend/src/hooks/')) return 'hook';
    if (rel.startsWith('frontend/src/lib/')) return 'frontend-lib';
    if (rel.startsWith('frontend/src/types/')) return 'types';
    if (basename === 'app.tsx') return 'app-entry';
    if (basename === 'index.css') return 'stylesheet';

    // Config files
    if (basename === 'package.json') return 'package-config';
    if (basename === 'tsconfig.json') return 'ts-config';
    if (basename === 'vite.config.ts' || basename === 'vitest.config.ts') return 'build-config';
    if (basename === '.env' || basename === '.env.example') return 'env-config';
    if (basename === 'requirements.txt') return 'python-deps';

    // CI/CD & Deploy
    if (rel.startsWith('.github/workflows/')) return 'ci-cd';
    if (basename === 'dockerfile') return 'docker';
    if (basename === 'docker-compose.yml') return 'docker-compose';
    if (basename === 'railway.toml' || basename === 'vercel.json') return 'deploy-config';

    // Documentation
    if (ext === '.md') return 'documentation';

    // Mobile
    if (rel.startsWith('mobile/')) return 'mobile';

    // Data files
    if (ext === '.json' && (rel.includes('data') || basename.includes('meme'))) return 'data';
    if (ext === '.json') return 'json-config';

    // Python files (generic)
    if (ext === '.py') return 'python-generic';

    // TypeScript/JavaScript files (generic)
    if (ext === '.ts' || ext === '.tsx' || ext === '.js') return 'typescript-generic';

    // Other
    if (ext === '.yml' || ext === '.yaml') return 'yaml-config';
    if (basename === '.gitignore') return 'gitignore';

    return 'other';
}

function getDomainLabel(filePath, workspaceRoot, isFolder = false) {
    if (isFolder) {
        const rel = path.relative(workspaceRoot, filePath).replace(/\\/g, '/');
        const folderName = path.basename(filePath).toLowerCase();

        if (folderName === 'tests') return 'Test Suite';
        if (folderName === 'api' || folderName === 'v1') return 'API Routes';
        if (folderName === 'services') return 'Services';
        if (folderName === 'models') return 'Data Models';
        if (folderName === 'core') return 'Core Modules';
        if (folderName === 'repositories') return 'Data Repositories';
        if (folderName === 'jobs') return 'Background Jobs';
        if (folderName === 'scripts') return 'Utility Scripts';
        if (folderName === 'components') return 'UI Components';
        if (folderName === 'hooks') return 'React Hooks';
        if (folderName === 'lib') return 'Utilities';
        if (folderName === 'types') return 'Type Definitions';
        if (folderName === 'ui') return 'UI Primitives';
        if (folderName === 'app') return 'Application';
        if (folderName === 'backend') return 'Backend';
        if (folderName === 'frontend') return 'Frontend';
        if (folderName === 'mobile') return 'Mobile App';
        if (folderName === 'data') return 'Data Files';
        if (folderName === 'src') return 'Source Code';
        if (folderName === 'workflows') return 'CI/CD Workflows';
        if (folderName === 'public') return 'Static Assets';
        if (folderName === 'pages') return 'Page Routes';
        if (rel.includes('md files')) return 'Documentation';
        return 'Folder';
    }

    const domain = detectDomain(filePath, workspaceRoot);
    const labels = {
        'python-test': 'Test Pass Rate',
        'frontend-test': 'Test Coverage',
        'test-config': 'Test Configuration',
        'api-route': 'API Implementation',
        'service': 'Service Quality',
        'model': 'Model Completeness',
        'core': 'Core Implementation',
        'repository': 'Repository Pattern',
        'background-job': 'Job Implementation',
        'script': 'Script Completeness',
        'data': 'Data Population',
        'database': 'Database Schema',
        'config': 'Configuration',
        'main-entry': 'App Entry Point',
        'ai-matcher': 'AI Matcher Quality',
        'ai-engine': 'AI Engine Quality',
        'ai-search': 'Semantic Search Quality',
        'component': 'Component Quality',
        'hook': 'Hook Implementation',
        'frontend-lib': 'Utility Quality',
        'types': 'Type Coverage',
        'app-entry': 'App Entry',
        'stylesheet': 'Style Coverage',
        'package-config': 'Package Config',
        'ts-config': 'TypeScript Config',
        'build-config': 'Build Config',
        'env-config': 'Environment Config',
        'python-deps': 'Dependencies',
        'ci-cd': 'Pipeline Coverage',
        'docker': 'Docker Quality',
        'docker-compose': 'Compose Config',
        'deploy-config': 'Deploy Config',
        'documentation': 'Documentation',
        'mobile': 'Mobile Implementation',
        'json-config': 'Config Completeness',
        'python-generic': 'Implementation',
        'typescript-generic': 'Implementation',
        'yaml-config': 'Config Quality',
    };
    return labels[domain] || 'File Quality';
}

// ─── Analysis Functions ─────────────────────────────────────────────────────

function readFileContent(filePath) {
    try {
        return fs.readFileSync(filePath, 'utf8');
    } catch {
        return '';
    }
}

// ── Python Test Files ───────────────────────────────────────────────────────
function analyzePythonTest(content, testResults) {
    const checks = [];
    const details = [];

    // If we have actual test results, use them
    if (testResults) {
        const total = testResults.passed + testResults.failed;
        if (total > 0) {
            const passRate = Math.round((testResults.passed / total) * 100);
            details.push(`Tests: ${testResults.passed}/${total} passed`);
            if (testResults.failed > 0) {
                details.push(`Failed: ${testResults.failures.join(', ')}`);
            }
            return {
                percentage: passRate,
                details: details
            };
        }
    }

    // Fallback: analyze test quality from code
    const testCount = (content.match(/def test_/g) || []).length;
    checks.push({ name: 'Has test functions', pass: testCount > 0, weight: 25 });
    details.push(`Test functions: ${testCount}`);

    const assertCount = (content.match(/assert\s|assertEqual|assertTrue|assertFalse|assertIn|assertRaises|pytest\.raises/g) || []).length;
    checks.push({ name: 'Has assertions', pass: assertCount > 0, weight: 20 });
    details.push(`Assertions: ${assertCount}`);

    const hasFixtures = /(@pytest\.fixture|@pytest\.mark)/g.test(content);
    checks.push({ name: 'Uses fixtures/marks', pass: hasFixtures, weight: 10 });

    const hasDocstrings = (content.match(/"""[\s\S]*?"""/g) || []).length > 0;
    checks.push({ name: 'Has docstrings', pass: hasDocstrings, weight: 10 });

    const hasParametrize = /@pytest\.mark\.parametrize/.test(content);
    checks.push({ name: 'Uses parametrize', pass: hasParametrize, weight: 5 });

    const hasExceptionTest = /pytest\.raises|assertRaises/.test(content);
    checks.push({ name: 'Tests exceptions', pass: hasExceptionTest, weight: 10 });

    const hasImports = /^(import|from)\s/m.test(content);
    checks.push({ name: 'Has imports', pass: hasImports, weight: 5 });

    const hasMocking = /mock|patch|MagicMock|Mock\(/.test(content);
    checks.push({ name: 'Uses mocking', pass: hasMocking, weight: 5 });

    const hasCleanup = /teardown|cleanup|yield/.test(content);
    checks.push({ name: 'Has cleanup/teardown', pass: hasCleanup, weight: 5 });

    // Bonus for high assertion density
    const assertDensity = testCount > 0 ? assertCount / testCount : 0;
    checks.push({ name: 'Good assertion density', pass: assertDensity >= 2, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python API Route Files ──────────────────────────────────────────────────
function analyzeApiRoute(content) {
    const checks = [];
    const details = [];

    const routeCount = (content.match(/@router\.(get|post|put|delete|patch)/gi) || []).length;
    checks.push({ name: 'Has route definitions', pass: routeCount > 0, weight: 20 });
    details.push(`Routes: ${routeCount}`);

    const hasResponseModel = /response_model\s*=/.test(content);
    checks.push({ name: 'Response models defined', pass: hasResponseModel, weight: 10 });

    const hasHTTPException = /HTTPException|raise.*HTTP/.test(content);
    checks.push({ name: 'Error handling', pass: hasHTTPException, weight: 15 });

    const hasValidation = /Body\(|Query\(|Path\(|Depends\(|BaseModel/.test(content);
    checks.push({ name: 'Input validation', pass: hasValidation, weight: 15 });

    const hasDocstrings = (content.match(/"""[\s\S]*?"""/g) || []).length > 0;
    checks.push({ name: 'Docstrings', pass: hasDocstrings, weight: 10 });

    const hasAuth = /Depends\(|get_current_user|verify_api_key|api_key/.test(content);
    checks.push({ name: 'Auth/Authorization', pass: hasAuth, weight: 10 });

    const hasTypeHints = /:\s*(str|int|float|bool|list|dict|List|Dict|Optional|Any)/.test(content);
    checks.push({ name: 'Type hints', pass: hasTypeHints, weight: 5 });

    const hasTryExcept = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Try/except blocks', pass: hasTryExcept, weight: 5 });

    const hasLogging = /logger\.|logging\.|log\./i.test(content);
    checks.push({ name: 'Logging', pass: hasLogging, weight: 5 });

    const hasStatusCodes = /status_code\s*=\s*\d|status\.HTTP/.test(content);
    checks.push({ name: 'Status codes', pass: hasStatusCodes, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python Service Files ────────────────────────────────────────────────────
function analyzeService(content) {
    const checks = [];
    const details = [];

    const classCount = (content.match(/^class\s+\w+/gm) || []).length;
    const funcCount = (content.match(/^\s*(?:def|async\s+def)\s+\w+/gm) || []).length;
    checks.push({ name: 'Has class/function definitions', pass: funcCount > 0, weight: 15 });
    details.push(`Classes: ${classCount}, Functions: ${funcCount}`);

    const hasDocstrings = (content.match(/"""[\s\S]*?"""/g) || []).length >= 1;
    checks.push({ name: 'Docstrings', pass: hasDocstrings, weight: 10 });

    const hasTryExcept = (content.match(/try:[\s\S]*?except/g) || []).length > 0;
    checks.push({ name: 'Error handling', pass: hasTryExcept, weight: 20 });

    const hasTypeHints = (content.match(/->\s*(str|int|float|bool|list|dict|List|Dict|Optional|Any|None)/g) || []).length > 0;
    checks.push({ name: 'Return type hints', pass: hasTypeHints, weight: 10 });

    const hasLogging = /logger\.|logging\.|log\./i.test(content);
    checks.push({ name: 'Logging', pass: hasLogging, weight: 10 });

    const hasAsync = /async\s+def/.test(content);
    checks.push({ name: 'Async support', pass: hasAsync, weight: 5 });

    const hasValidation = /validate|ValueError|TypeError|assert\s/.test(content);
    checks.push({ name: 'Input validation', pass: hasValidation, weight: 10 });

    const hasConstants = /^[A-Z_]+\s*=\s*/m.test(content);
    checks.push({ name: 'Constants defined', pass: hasConstants, weight: 5 });

    const hasPrivateMethods = /def\s+_\w+/.test(content);
    checks.push({ name: 'Encapsulation (private methods)', pass: hasPrivateMethods, weight: 5 });

    // Size-based bonus: larger services that have substantial code
    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial implementation', pass: lineCount > 30, weight: 10 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python Model Files ──────────────────────────────────────────────────────
function analyzeModel(content) {
    const checks = [];
    const details = [];

    // Detect if this is Pydantic or SQLAlchemy
    const isPydantic = /BaseModel|Field\(/.test(content);
    const isSQLAlchemy = /DeclarativeBase|__tablename__|Column\(/.test(content);

    if (isPydantic) {
        // Pydantic model analysis
        const classCount = (content.match(/class\s+\w+\(BaseModel\)/g) || []).length;
        checks.push({ name: 'Schema classes defined', pass: classCount > 0, weight: 15 });
        details.push(`Schema classes: ${classCount}`);

        const fieldCount = (content.match(/^\s+\w+\s*:/gm) || []).length;
        checks.push({ name: 'Fields defined', pass: fieldCount > 0, weight: 20 });
        details.push(`Fields: ${fieldCount}`);

        const hasTypeHints = /:\s*(str|int|float|bool|List|Dict|Optional|Any)/.test(content);
        checks.push({ name: 'Type annotations', pass: hasTypeHints, weight: 15 });

        const hasFieldValidation = /Field\(/.test(content);
        checks.push({ name: 'Field validation', pass: hasFieldValidation, weight: 10 });

        const hasDefaults = /default\s*=|default_factory|=\s*\[|=\s*None|=\s*0|=\s*""/.test(content);
        checks.push({ name: 'Default values', pass: hasDefaults, weight: 10 });

        const hasOptional = /Optional\[/.test(content);
        checks.push({ name: 'Optional fields', pass: hasOptional, weight: 5 });

        const hasImports = /from\s+(typing|pydantic)\s+import/.test(content);
        checks.push({ name: 'Proper imports', pass: hasImports, weight: 5 });

        const hasPatterns = /pattern\s*=|regex|min_length|max_length|ge=|le=|gt=|lt=/.test(content);
        checks.push({ name: 'Validation constraints', pass: hasPatterns, weight: 10 });

        const hasDocstring = /"""[\s\S]*?"""/.test(content);
        checks.push({ name: 'Docstrings', pass: hasDocstring, weight: 5 });

        const hasMultipleModels = classCount >= 2;
        checks.push({ name: 'Multiple schemas (request/response)', pass: hasMultipleModels, weight: 5 });
    } else {
        // SQLAlchemy model analysis
        const hasBase = /Base\)|DeclarativeBase/.test(content);
        checks.push({ name: 'Inherits from Base', pass: hasBase, weight: 15 });

        const columnCount = (content.match(/Column\(|mapped_column\(/g) || []).length;
        checks.push({ name: 'Has columns defined', pass: columnCount > 0, weight: 20 });
        details.push(`Columns: ${columnCount}`);

        const hasRelationships = /relationship\(|ForeignKey\(/.test(content);
        checks.push({ name: 'Relationships defined', pass: hasRelationships, weight: 15 });

        const hasTableName = /__tablename__/.test(content);
        checks.push({ name: 'Table name set', pass: hasTableName, weight: 10 });

        const hasRepr = /__repr__|__str__/.test(content);
        checks.push({ name: 'String representation', pass: hasRepr, weight: 5 });

        const hasValidators = /validator|@validates|check_constraint/.test(content);
        checks.push({ name: 'Validators', pass: hasValidators, weight: 10 });

        const hasIndexes = /Index\(|index\s*=\s*True/.test(content);
        checks.push({ name: 'Indexes defined', pass: hasIndexes, weight: 10 });

        const hasDefaults = /default\s*=|server_default/.test(content);
        checks.push({ name: 'Default values', pass: hasDefaults, weight: 5 });

        const hasDocstring = /"""[\s\S]*?"""/.test(content);
        checks.push({ name: 'Docstrings', pass: hasDocstring, weight: 5 });

        const hasNullable = /nullable\s*=/.test(content);
        checks.push({ name: 'Nullable constraints', pass: hasNullable, weight: 5 });
    }

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python Core Module Files ────────────────────────────────────────────────
function analyzeCore(content) {
    const checks = [];
    const details = [];

    const funcCount = (content.match(/^\s*(?:def|async\s+def)\s+\w+/gm) || []).length;
    checks.push({ name: 'Has function definitions', pass: funcCount > 0, weight: 15 });
    details.push(`Functions: ${funcCount}`);

    const hasTryExcept = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Error handling', pass: hasTryExcept, weight: 20 });

    const hasDocstrings = /"""[\s\S]*?"""/.test(content);
    checks.push({ name: 'Docstrings', pass: hasDocstrings, weight: 10 });

    const hasTypeHints = /:\s*(str|int|float|bool|list|dict|List|Dict|Optional|Any)/.test(content);
    checks.push({ name: 'Type hints', pass: hasTypeHints, weight: 10 });

    const hasLogging = /logger\.|logging\.|log\./i.test(content);
    checks.push({ name: 'Logging', pass: hasLogging, weight: 10 });

    const hasConfig = /settings\.|config\.|os\.environ|os\.getenv/.test(content);
    checks.push({ name: 'Configuration usage', pass: hasConfig, weight: 10 });

    const hasDecorators = /@\w+/.test(content);
    checks.push({ name: 'Decorator patterns', pass: hasDecorators, weight: 5 });

    const hasImports = /^(import|from)\s/m.test(content);
    checks.push({ name: 'Proper imports', pass: hasImports, weight: 5 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial implementation', pass: lineCount > 20, weight: 10 });

    const hasConstants = /^[A-Z_]+\s*=\s*/m.test(content);
    checks.push({ name: 'Constants/config', pass: hasConstants, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python Repository Files ─────────────────────────────────────────────────
function analyzeRepository(content) {
    const checks = [];
    const details = [];

    const hasClass = /^class\s+\w+/m.test(content);
    checks.push({ name: 'Repository class defined', pass: hasClass, weight: 15 });

    const hasCRUD = /def\s+(get|create|update|delete|find|list|add|remove)/i.test(content);
    checks.push({ name: 'CRUD operations', pass: hasCRUD, weight: 20 });

    const hasAsync = /async\s+def/.test(content);
    checks.push({ name: 'Async methods', pass: hasAsync, weight: 10 });

    const hasTryExcept = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Error handling', pass: hasTryExcept, weight: 15 });

    const hasQuery = /query|select|filter|session/.test(content);
    checks.push({ name: 'Database queries', pass: hasQuery, weight: 15 });

    const hasTypeHints = /->\s*(str|int|float|bool|list|dict|List|Dict|Optional|Any|None)/.test(content);
    checks.push({ name: 'Return type hints', pass: hasTypeHints, weight: 10 });

    const hasDocstring = /"""[\s\S]*?"""/.test(content);
    checks.push({ name: 'Docstrings', pass: hasDocstring, weight: 10 });

    const hasPagination = /offset|limit|page|skip/.test(content);
    checks.push({ name: 'Pagination support', pass: hasPagination, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python Script Files ─────────────────────────────────────────────────────
function analyzeScript(content) {
    const checks = [];
    const details = [];

    const hasMainGuard = /if\s+__name__\s*==\s*['"]__main__['"]/.test(content);
    checks.push({ name: 'Main guard', pass: hasMainGuard, weight: 15 });

    const hasArgparse = /argparse|sys\.argv|click/.test(content);
    checks.push({ name: 'Argument parsing', pass: hasArgparse, weight: 10 });

    const hasTryExcept = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Error handling', pass: hasTryExcept, weight: 20 });

    const hasLogging = /logger\.|logging\.|print\(/.test(content);
    checks.push({ name: 'Output/logging', pass: hasLogging, weight: 10 });

    const hasDocstring = /"""[\s\S]*?"""/.test(content);
    checks.push({ name: 'Docstrings', pass: hasDocstring, weight: 10 });

    const funcCount = (content.match(/^\s*def\s+\w+/gm) || []).length;
    checks.push({ name: 'Function decomposition', pass: funcCount >= 2, weight: 10 });
    details.push(`Functions: ${funcCount}`);

    const hasImports = /^(import|from)\s/m.test(content);
    checks.push({ name: 'Proper imports', pass: hasImports, weight: 5 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial code', pass: lineCount > 15, weight: 10 });

    const hasProgress = /tqdm|progress|bar|step|done/.test(content);
    checks.push({ name: 'Progress indicators', pass: hasProgress, weight: 5 });

    const hasComments = /#\s*\w/.test(content);
    checks.push({ name: 'Code comments', pass: hasComments, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── TypeScript/TSX Component Files ──────────────────────────────────────────
function analyzeComponent(content) {
    const checks = [];
    const details = [];

    const hasInterface = /interface\s+\w+Props|type\s+\w+Props/.test(content);
    checks.push({ name: 'Props interface/type', pass: hasInterface, weight: 15 });

    const hasComponent = /function\s+\w+|const\s+\w+\s*[:=]\s*(?:React\.FC|.*=>)/.test(content);
    checks.push({ name: 'Component definition', pass: hasComponent, weight: 15 });

    const hasErrorHandling = /try\s*{|catch\s*\(|\.catch\(|onError|ErrorBoundary/.test(content);
    checks.push({ name: 'Error handling', pass: hasErrorHandling, weight: 10 });

    const hasLoadingState = /loading|isLoading|skeleton|Skeleton|spinner|Spinner/.test(content);
    checks.push({ name: 'Loading state', pass: hasLoadingState, weight: 10 });

    const hasAccessibility = /aria-|role=|tabIndex|alt=|title=/.test(content);
    checks.push({ name: 'Accessibility attrs', pass: hasAccessibility, weight: 10 });

    const hasMemoization = /React\.memo|useMemo|useCallback|memo\(/.test(content);
    checks.push({ name: 'Memoization', pass: hasMemoization, weight: 5 });

    const hasEventHandlers = /onClick|onChange|onSubmit|onKeyDown|onFocus/.test(content);
    checks.push({ name: 'Event handlers', pass: hasEventHandlers, weight: 5 });

    const hasState = /useState|useReducer|useContext/.test(content);
    checks.push({ name: 'State management', pass: hasState, weight: 5 });

    const hasEffects = /useEffect/.test(content);
    checks.push({ name: 'Side effects', pass: hasEffects, weight: 5 });

    const hasExport = /export\s+(default|{)/.test(content);
    checks.push({ name: 'Proper exports', pass: hasExport, weight: 5 });

    const hasResponsive = /className.*sm:|md:|lg:|xl:|@media|responsive|mobile|desktop/.test(content);
    checks.push({ name: 'Responsive design', pass: hasResponsive, weight: 5 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial component', pass: lineCount > 20, weight: 5 });

    const hasKeyProp = /key=\{|key={/.test(content);
    const hasList = /\.map\(/.test(content);
    if (hasList) {
        checks.push({ name: 'Key props in lists', pass: hasKeyProp, weight: 5 });
    }

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── TypeScript Hook Files ───────────────────────────────────────────────────
function analyzeHook(content) {
    const checks = [];
    const details = [];

    const hasHookPattern = /export\s+(function|const)\s+use\w+/.test(content);
    checks.push({ name: 'Hook pattern', pass: hasHookPattern, weight: 20 });

    const hasState = /useState|useReducer/.test(content);
    checks.push({ name: 'State management', pass: hasState, weight: 15 });

    const hasEffect = /useEffect/.test(content);
    checks.push({ name: 'Side effects', pass: hasEffect, weight: 10 });

    const hasCleanup = /return\s*\(\s*\)\s*=>|return\s*\(\)\s*=>/.test(content);
    checks.push({ name: 'Effect cleanup', pass: hasCleanup, weight: 10 });

    const hasErrorHandling = /try\s*{|catch\s*\(|error|Error/.test(content);
    checks.push({ name: 'Error handling', pass: hasErrorHandling, weight: 15 });

    const hasTypeAnnotation = /:\s*(string|number|boolean|any|void|Promise|Array|Record)/.test(content);
    checks.push({ name: 'Type annotations', pass: hasTypeAnnotation, weight: 10 });

    const hasMemoization = /useMemo|useCallback|useRef/.test(content);
    checks.push({ name: 'Memoization/refs', pass: hasMemoization, weight: 10 });

    const hasExport = /export\s/.test(content);
    checks.push({ name: 'Proper export', pass: hasExport, weight: 5 });

    const hasLoadingState = /loading|isLoading|pending/.test(content);
    checks.push({ name: 'Loading state', pass: hasLoadingState, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Frontend Lib/Utility Files ──────────────────────────────────────────────
function analyzeFrontendLib(content) {
    const checks = [];
    const details = [];

    const hasExports = (content.match(/export\s+(function|const|class|type|interface)/g) || []).length;
    checks.push({ name: 'Has exports', pass: hasExports > 0, weight: 20 });
    details.push(`Exports: ${hasExports}`);

    const hasTypeAnnotations = /:\s*(string|number|boolean|any|void|Promise|Record)/.test(content);
    checks.push({ name: 'Type safety', pass: hasTypeAnnotations, weight: 15 });

    const hasErrorHandling = /try\s*{|catch\s*\(|throw\s/.test(content);
    checks.push({ name: 'Error handling', pass: hasErrorHandling, weight: 15 });

    const hasDocComments = /\/\*\*[\s\S]*?\*\/|\/\//.test(content);
    checks.push({ name: 'Documentation', pass: hasDocComments, weight: 10 });

    const hasFunctions = (content.match(/(?:function|const\s+\w+\s*=\s*(?:\(|async))/g) || []).length;
    checks.push({ name: 'Function definitions', pass: hasFunctions > 0, weight: 15 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial code', pass: lineCount > 10, weight: 10 });

    const hasAsync = /async|await|Promise/.test(content);
    checks.push({ name: 'Async support', pass: hasAsync, weight: 5 });

    const hasConstants = /const\s+[A-Z_]+\s*=/.test(content);
    checks.push({ name: 'Constants defined', pass: hasConstants, weight: 5 });

    const hasNullChecks = /\?\.|!= null|!== null|!== undefined/.test(content);
    checks.push({ name: 'Null safety', pass: hasNullChecks, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── CI/CD Workflow Files ────────────────────────────────────────────────────
function analyzeCICD(content) {
    const checks = [];
    const details = [];

    const hasName = /^name:/m.test(content);
    checks.push({ name: 'Workflow name', pass: hasName, weight: 10 });

    const hasTrigger = /on:|push:|pull_request:|schedule:|workflow_dispatch:/.test(content);
    checks.push({ name: 'Trigger defined', pass: hasTrigger, weight: 15 });

    const hasJobs = /^jobs:/m.test(content);
    checks.push({ name: 'Jobs defined', pass: hasJobs, weight: 15 });

    const hasSteps = /steps:/.test(content);
    checks.push({ name: 'Steps defined', pass: hasSteps, weight: 15 });

    const hasCheckout = /actions\/checkout/.test(content);
    checks.push({ name: 'Checkout action', pass: hasCheckout, weight: 5 });

    const hasSetup = /setup-node|setup-python|actions\/setup/.test(content);
    checks.push({ name: 'Environment setup', pass: hasSetup, weight: 10 });

    const hasCaching = /actions\/cache|cache:/.test(content);
    checks.push({ name: 'Dependency caching', pass: hasCaching, weight: 10 });

    const hasEnvVars = /env:|secrets\./.test(content);
    checks.push({ name: 'Environment variables', pass: hasEnvVars, weight: 10 });

    const hasTests = /test|pytest|vitest|jest/.test(content);
    checks.push({ name: 'Test execution', pass: hasTests, weight: 5 });

    const hasNotification = /slack|email|notification|notify/.test(content);
    checks.push({ name: 'Notifications', pass: hasNotification, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Docker Files ────────────────────────────────────────────────────────────
function analyzeDocker(content) {
    const checks = [];

    const hasFrom = /^FROM\s/m.test(content);
    checks.push({ name: 'Base image', pass: hasFrom, weight: 20 });

    const hasWorkdir = /WORKDIR/.test(content);
    checks.push({ name: 'Working directory', pass: hasWorkdir, weight: 10 });

    const hasCopy = /COPY|ADD/.test(content);
    checks.push({ name: 'File copying', pass: hasCopy, weight: 10 });

    const hasExpose = /EXPOSE/.test(content);
    checks.push({ name: 'Port exposed', pass: hasExpose, weight: 10 });

    const hasCmd = /CMD|ENTRYPOINT/.test(content);
    checks.push({ name: 'Entrypoint', pass: hasCmd, weight: 15 });

    const hasMultiStage = (content.match(/^FROM\s/gm) || []).length > 1;
    checks.push({ name: 'Multi-stage build', pass: hasMultiStage, weight: 10 });

    const hasHealthcheck = /HEALTHCHECK/.test(content);
    checks.push({ name: 'Health check', pass: hasHealthcheck, weight: 10 });

    const hasEnv = /ENV\s/.test(content);
    checks.push({ name: 'Environment vars', pass: hasEnv, weight: 5 });

    const hasUser = /USER\s(?!root)/.test(content);
    checks.push({ name: 'Non-root user', pass: hasUser, weight: 5 });

    const hasLabels = /LABEL/.test(content);
    checks.push({ name: 'Labels/metadata', pass: hasLabels, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details: [] };
}

// ── Documentation Files ─────────────────────────────────────────────────────
function analyzeDocumentation(content) {
    const checks = [];
    const details = [];

    const hasTitle = /^#\s+.+/m.test(content);
    checks.push({ name: 'Has title', pass: hasTitle, weight: 15 });

    const sectionCount = (content.match(/^##\s+/gm) || []).length;
    checks.push({ name: 'Has sections', pass: sectionCount >= 2, weight: 15 });
    details.push(`Sections: ${sectionCount}`);

    const hasCodeBlocks = /```/.test(content);
    checks.push({ name: 'Code examples', pass: hasCodeBlocks, weight: 10 });

    const hasTables = /\|.*\|.*\|/.test(content);
    checks.push({ name: 'Tables', pass: hasTables, weight: 10 });

    const hasLinks = /\[.*\]\(.*\)/.test(content);
    checks.push({ name: 'Links/references', pass: hasLinks, weight: 10 });

    const hasMermaid = /```mermaid/.test(content);
    checks.push({ name: 'Diagrams', pass: hasMermaid, weight: 5 });

    const hasLists = /^[\s]*[-*+]\s/m.test(content);
    checks.push({ name: 'Lists', pass: hasLists, weight: 5 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial content', pass: lineCount > 20, weight: 15 });
    details.push(`Lines: ${lineCount}`);

    const hasEmoji = /[\u{1F300}-\u{1F9FF}]|✅|❌|⏳|📊|📋|🔧|⚠️|💡/u.test(content);
    checks.push({ name: 'Visual formatting', pass: hasEmoji, weight: 5 });

    const hasChecklist = /- \[[ x]\]/.test(content);
    checks.push({ name: 'Checklists', pass: hasChecklist, weight: 5 });

    const hasBlockquote = /^>/.test(content);
    checks.push({ name: 'Notes/callouts', pass: hasBlockquote, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Config/JSON Files ───────────────────────────────────────────────────────
function analyzeJsonConfig(content, basename) {
    const checks = [];
    const details = [];

    let parsed;
    try {
        parsed = JSON.parse(content);
        checks.push({ name: 'Valid JSON', pass: true, weight: 20 });
    } catch {
        return { percentage: 30, details: ['Invalid JSON'] };
    }

    const keyCount = typeof parsed === 'object' ? Object.keys(parsed).length : 0;
    checks.push({ name: 'Has entries', pass: keyCount > 0, weight: 20 });
    details.push(`Keys: ${keyCount}`);

    // Domain-specific checks
    if (basename === 'package.json') {
        checks.push({ name: 'Has name', pass: !!parsed.name, weight: 5 });
        checks.push({ name: 'Has version', pass: !!parsed.version, weight: 5 });
        checks.push({ name: 'Has scripts', pass: !!parsed.scripts && Object.keys(parsed.scripts).length > 0, weight: 15 });
        checks.push({ name: 'Has dependencies', pass: !!(parsed.dependencies || parsed.devDependencies), weight: 10 });
        const scriptCount = parsed.scripts ? Object.keys(parsed.scripts).length : 0;
        details.push(`Scripts: ${scriptCount}`);
    } else if (basename === 'tsconfig.json') {
        checks.push({ name: 'Compiler options', pass: !!parsed.compilerOptions, weight: 20 });
        checks.push({ name: 'Strict mode', pass: parsed.compilerOptions?.strict === true, weight: 10 });
        checks.push({ name: 'Include paths', pass: !!parsed.include, weight: 10 });
    } else if (basename === 'memes.json') {
        const recordCount = Array.isArray(parsed) ? parsed.length : keyCount;
        checks.push({ name: 'Substantial data (>50)', pass: recordCount > 50, weight: 20 });
        checks.push({ name: 'Rich data (>100)', pass: recordCount > 100, weight: 15 });
        details.push(`Records: ${recordCount}`);
    } else if (basename === 'vercel.json') {
        checks.push({ name: 'Has builds/routes', pass: !!(parsed.builds || parsed.routes || parsed.rewrites), weight: 20 });
        checks.push({ name: 'Has headers', pass: !!parsed.headers, weight: 10 });
    } else {
        // Generic JSON checks
        const hasNonEmpty = Object.values(parsed).some(v => v !== null && v !== '' && v !== undefined);
        checks.push({ name: 'Non-empty values', pass: hasNonEmpty, weight: 20 });
        const depth = getObjectDepth(parsed);
        checks.push({ name: 'Structured data', pass: depth > 1, weight: 10 });
    }

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Environment Config Files ────────────────────────────────────────────────
function analyzeEnvConfig(content) {
    const checks = [];
    const details = [];

    const lines = content.split('\n').filter(l => l.trim() && !l.trim().startsWith('#'));
    const keyCount = lines.length;
    details.push(`Variables: ${keyCount}`);

    checks.push({ name: 'Has variables', pass: keyCount > 0, weight: 20 });
    checks.push({ name: 'Multiple variables (>5)', pass: keyCount > 5, weight: 10 });
    checks.push({ name: 'Comprehensive (>10)', pass: keyCount > 10, weight: 10 });

    // Check for key categories
    const hasDBConfig = /DATABASE|DB_|SQLITE|POSTGRES/i.test(content);
    checks.push({ name: 'Database config', pass: hasDBConfig, weight: 10 });

    const hasAPIKeys = /API_KEY|SECRET|TOKEN|KEY/i.test(content);
    checks.push({ name: 'API keys/secrets', pass: hasAPIKeys, weight: 10 });

    const hasServerConfig = /HOST|PORT|URL|CORS/i.test(content);
    checks.push({ name: 'Server config', pass: hasServerConfig, weight: 10 });

    const hasAIConfig = /OPENAI|GROQ|HF_|HUGGING|MODEL|EMBEDDING/i.test(content);
    checks.push({ name: 'AI/ML config', pass: hasAIConfig, weight: 10 });

    const hasCacheConfig = /REDIS|CACHE|UPSTASH/i.test(content);
    checks.push({ name: 'Cache config', pass: hasCacheConfig, weight: 5 });

    const hasComments = /^#\s*\w/m.test(content);
    checks.push({ name: 'Documented (comments)', pass: hasComments, weight: 5 });

    const hasValues = lines.filter(l => l.includes('=') && l.split('=')[1]?.trim().length > 0).length;
    const valueRatio = keyCount > 0 ? hasValues / keyCount : 0;
    checks.push({ name: 'Values populated', pass: valueRatio > 0.5, weight: 10 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Python Dependencies (requirements.txt) ──────────────────────────────────
function analyzePythonDeps(content) {
    const checks = [];
    const details = [];

    const deps = content.split('\n').filter(l => l.trim() && !l.trim().startsWith('#'));
    const depCount = deps.length;
    details.push(`Dependencies: ${depCount}`);

    checks.push({ name: 'Has dependencies', pass: depCount > 0, weight: 20 });
    checks.push({ name: 'Multiple deps (>5)', pass: depCount > 5, weight: 10 });

    const hasPinned = deps.some(d => /==/.test(d));
    checks.push({ name: 'Version pinning', pass: hasPinned, weight: 15 });

    const hasFastAPI = /fastapi/i.test(content);
    checks.push({ name: 'FastAPI (core)', pass: hasFastAPI, weight: 10 });

    const hasDB = /sqlalchemy|sqlite|postgres|prisma/i.test(content);
    checks.push({ name: 'Database deps', pass: hasDB, weight: 10 });

    const hasML = /torch|transformers|sentence.transformers|openai|groq/i.test(content);
    checks.push({ name: 'ML/AI deps', pass: hasML, weight: 10 });

    const hasTesting = /pytest|coverage/i.test(content);
    checks.push({ name: 'Testing deps', pass: hasTesting, weight: 10 });

    const hasUtils = /uvicorn|pydantic|httpx|requests/i.test(content);
    checks.push({ name: 'Utility deps', pass: hasUtils, weight: 10 });

    const hasComments = /#/.test(content);
    checks.push({ name: 'Comments', pass: hasComments, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── CSS/Stylesheet Files ────────────────────────────────────────────────────
function analyzeStylesheet(content) {
    const checks = [];
    const details = [];

    const ruleCount = (content.match(/{/g) || []).length;
    checks.push({ name: 'CSS rules defined', pass: ruleCount > 0, weight: 15 });
    details.push(`Rules: ${ruleCount}`);

    const hasVariables = /--\w+/.test(content);
    checks.push({ name: 'CSS variables', pass: hasVariables, weight: 15 });

    const hasMediaQueries = /@media/.test(content);
    checks.push({ name: 'Responsive (media queries)', pass: hasMediaQueries, weight: 15 });

    const hasAnimations = /@keyframes|animation|transition/.test(content);
    checks.push({ name: 'Animations/transitions', pass: hasAnimations, weight: 10 });

    const hasDarkMode = /dark|prefers-color-scheme/.test(content);
    checks.push({ name: 'Dark mode support', pass: hasDarkMode, weight: 10 });

    const hasFlexGrid = /display:\s*(flex|grid)/.test(content);
    checks.push({ name: 'Flexbox/Grid layout', pass: hasFlexGrid, weight: 10 });

    const hasHover = /:hover|:focus|:active/.test(content);
    checks.push({ name: 'Interactive states', pass: hasHover, weight: 5 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial styles', pass: lineCount > 50, weight: 10 });

    const hasImports = /@import|@font-face/.test(content);
    checks.push({ name: 'External resources', pass: hasImports, weight: 5 });

    const hasComments = /\/\*[\s\S]*?\*\//.test(content);
    checks.push({ name: 'Comments', pass: hasComments, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Database Module ─────────────────────────────────────────────────────────
function analyzeDatabase(content) {
    const checks = [];
    const details = [];

    const hasEngine = /create_engine|engine/.test(content);
    checks.push({ name: 'Engine setup', pass: hasEngine, weight: 15 });

    const hasSession = /sessionmaker|Session|session/.test(content);
    checks.push({ name: 'Session management', pass: hasSession, weight: 10 });

    const hasBase = /Base|DeclarativeBase|declarative_base/.test(content);
    checks.push({ name: 'Base model', pass: hasBase, weight: 10 });

    const tableCount = (content.match(/class\s+\w+.*Base/g) || []).length;
    checks.push({ name: 'Table definitions', pass: tableCount > 0, weight: 15 });
    details.push(`Tables: ${tableCount}`);

    const hasIndexes = /Index\(|index\s*=\s*True/.test(content);
    checks.push({ name: 'Indexes', pass: hasIndexes, weight: 10 });

    const hasMigration = /migration|alembic|migrate|upgrade|downgrade/.test(content);
    checks.push({ name: 'Migration support', pass: hasMigration, weight: 10 });

    const hasErrorHandling = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Error handling', pass: hasErrorHandling, weight: 10 });

    const hasForeignKeys = /ForeignKey/.test(content);
    checks.push({ name: 'Foreign keys', pass: hasForeignKeys, weight: 5 });

    const hasRelationships = /relationship\(/.test(content);
    checks.push({ name: 'Relationships', pass: hasRelationships, weight: 5 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Comprehensive schema', pass: lineCount > 100, weight: 10 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── AI Module Files ─────────────────────────────────────────────────────────
function analyzeAIModule(content) {
    const checks = [];
    const details = [];

    const hasEmbeddings = /embedding|encode|vector|cosine_similarity/.test(content);
    checks.push({ name: 'Embedding/vector support', pass: hasEmbeddings, weight: 10 });

    const hasLLM = /openai|groq|llm|generate|completion|prompt/.test(content);
    checks.push({ name: 'LLM integration', pass: hasLLM, weight: 10 });

    const hasTryExcept = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Error handling', pass: hasTryExcept, weight: 10 });

    const hasDocstrings = /"""[\s\S]*?"""/.test(content);
    checks.push({ name: 'Docstrings', pass: hasDocstrings, weight: 10 });

    const hasTypeHints = /->\s*(str|int|float|bool|list|dict|List|Dict|Optional|Any|None)/.test(content);
    checks.push({ name: 'Type hints', pass: hasTypeHints, weight: 10 });

    const hasScoring = /score|rank|similarity|distance|weight|match/.test(content);
    checks.push({ name: 'Scoring/ranking logic', pass: hasScoring, weight: 10 });

    const hasCaching = /cache|lru_cache|functools/.test(content);
    checks.push({ name: 'Result caching', pass: hasCaching, weight: 5 });

    const funcCount = (content.match(/^\s*(?:def|async\s+def)\s+\w+/gm) || []).length;
    checks.push({ name: 'Function decomposition', pass: funcCount >= 2, weight: 10 });
    details.push(`Functions: ${funcCount}`);

    const hasLogging = /logger\.|logging\.|log\./i.test(content);
    checks.push({ name: 'Logging', pass: hasLogging, weight: 5 });

    // Credit for rule/pattern/constant definitions (rule_engine, matcher, etc.)
    const hasRulesOrPatterns = /RULES|PATTERNS|KEYWORDS|CATEGORIES|@dataclass|re\.compile|regex/.test(content);
    checks.push({ name: 'Rules/patterns defined', pass: hasRulesOrPatterns, weight: 10 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial implementation', pass: lineCount > 50, weight: 5 });

    // Credit for using dataclasses or structured data
    const hasDataStructures = /dataclass|namedtuple|TypedDict|Enum|dict\[|list\[/.test(content);
    checks.push({ name: 'Structured data types', pass: hasDataStructures, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Data Files ──────────────────────────────────────────────────────────────
function analyzeDataFile(filePath, content) {
    const ext = path.extname(filePath).toLowerCase();
    const basename = path.basename(filePath).toLowerCase();

    if (ext === '.json') {
        try {
            const parsed = JSON.parse(content);
            const recordCount = Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length;

            // For memes.json, expect substantial data
            if (basename.includes('meme')) {
                if (recordCount >= 100) return { percentage: 95, details: [`Records: ${recordCount}`] };
                if (recordCount >= 50) return { percentage: 80, details: [`Records: ${recordCount}`] };
                if (recordCount >= 20) return { percentage: 65, details: [`Records: ${recordCount}`] };
                return { percentage: 40, details: [`Records: ${recordCount} (need more)`] };
            }

            // For embeddings, check size
            if (basename.includes('embedding')) {
                if (recordCount >= 100) return { percentage: 92, details: [`Embeddings: ${recordCount}`] };
                if (recordCount >= 50) return { percentage: 75, details: [`Embeddings: ${recordCount}`] };
                return { percentage: 50, details: [`Embeddings: ${recordCount} (need more)`] };
            }

            return { percentage: recordCount > 0 ? 85 : 40, details: [`Entries: ${recordCount}`] };
        } catch {
            return { percentage: 30, details: ['Invalid JSON'] };
        }
    }

    if (ext === '.py' && basename.includes('dataset')) {
        const lineCount = content.split('\n').length;
        if (lineCount > 200) return { percentage: 90, details: [`Lines: ${lineCount}`] };
        if (lineCount > 50) return { percentage: 75, details: [`Lines: ${lineCount}`] };
        return { percentage: 50, details: [`Lines: ${lineCount}`] };
    }

    // Binary/DB files
    try {
        const stats = fs.statSync(filePath);
        const sizeMB = stats.size / (1024 * 1024);
        if (sizeMB > 1) return { percentage: 88, details: [`Size: ${sizeMB.toFixed(1)}MB`] };
        if (sizeMB > 0.1) return { percentage: 72, details: [`Size: ${(sizeMB * 1024).toFixed(0)}KB`] };
        return { percentage: 50, details: [`Size: ${stats.size}B`] };
    } catch {
        return { percentage: 40, details: [] };
    }
}

// ── Init/Config Files ───────────────────────────────────────────────────────
function analyzeInitFile(content) {
    if (!content.trim()) {
        return { percentage: 60, details: ['Empty __init__.py (acceptable)'] };
    }

    const checks = [];
    const hasImports = /from\s+\.|import\s/.test(content);
    checks.push({ name: 'Re-exports', pass: hasImports, weight: 40 });

    const has__all__ = /__all__/.test(content);
    checks.push({ name: '__all__ defined', pass: has__all__, weight: 20 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Has content', pass: lineCount > 3, weight: 20 });

    const hasDocstring = /"""[\s\S]*?"""/.test(content);
    checks.push({ name: 'Module docstring', pass: hasDocstring, weight: 20 });

    return { percentage: calcWeightedPercentage(checks), details: [] };
}

// ── YAML Config Files ───────────────────────────────────────────────────────
function analyzeYamlConfig(content) {
    const checks = [];
    const lineCount = content.split('\n').filter(l => l.trim() && !l.trim().startsWith('#')).length;

    checks.push({ name: 'Has content', pass: lineCount > 0, weight: 25 });
    checks.push({ name: 'Substantial config', pass: lineCount > 5, weight: 20 });
    checks.push({ name: 'Has comments', pass: /#/.test(content), weight: 10 });
    checks.push({ name: 'Nested structure', pass: /^\s{2,}\w/m.test(content), weight: 15 });
    checks.push({ name: 'Key-value pairs', pass: /\w+:\s/.test(content), weight: 15 });
    checks.push({ name: 'Uses variables', pass: /\$\{|\{\{/.test(content), weight: 10 });
    checks.push({ name: 'Multi-line', pass: lineCount > 10, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details: [`Lines: ${lineCount}`] };
}

// ── Deploy Config Files ─────────────────────────────────────────────────────
function analyzeDeployConfig(content, basename) {
    const checks = [];

    if (basename === 'railway.toml') {
        const hasBuilder = /builder|nixpacks/.test(content);
        checks.push({ name: 'Builder defined', pass: hasBuilder, weight: 25 });
        const hasStart = /startCommand|start/.test(content);
        checks.push({ name: 'Start command', pass: hasStart, weight: 25 });
        const hasBuild = /buildCommand|build/.test(content);
        checks.push({ name: 'Build command', pass: hasBuild, weight: 25 });
        const hasEnv = /env|variable/.test(content);
        checks.push({ name: 'Env config', pass: hasEnv, weight: 15 });
        checks.push({ name: 'Has content', pass: content.trim().length > 10, weight: 10 });
    } else if (basename === 'vercel.json') {
        return analyzeJsonConfig(content, basename);
    } else {
        checks.push({ name: 'Has content', pass: content.trim().length > 10, weight: 50 });
        checks.push({ name: 'Structured', pass: content.split('\n').length > 3, weight: 50 });
    }

    return { percentage: calcWeightedPercentage(checks), details: [] };
}

// ── Generic Python File ─────────────────────────────────────────────────────
function analyzeGenericPython(content) {
    const checks = [];
    const details = [];

    const funcCount = (content.match(/^\s*(?:def|async\s+def)\s+\w+/gm) || []).length;
    checks.push({ name: 'Has functions', pass: funcCount > 0, weight: 15 });
    details.push(`Functions: ${funcCount}`);

    const hasDocstring = /"""[\s\S]*?"""/.test(content);
    checks.push({ name: 'Docstrings', pass: hasDocstring, weight: 10 });

    const hasTryExcept = /try:[\s\S]*?except/.test(content);
    checks.push({ name: 'Error handling', pass: hasTryExcept, weight: 15 });

    const hasImports = /^(import|from)\s/m.test(content);
    checks.push({ name: 'Imports', pass: hasImports, weight: 10 });

    const hasTypeHints = /:\s*(str|int|float|bool|list|dict|List|Dict|Optional|Any)/.test(content);
    checks.push({ name: 'Type hints', pass: hasTypeHints, weight: 10 });

    const hasLogging = /logger\.|logging\.|print\(/.test(content);
    checks.push({ name: 'Logging/output', pass: hasLogging, weight: 10 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial code', pass: lineCount > 15, weight: 10 });

    const hasMainGuard = /if\s+__name__\s*==\s*['"]__main__['"]/.test(content);
    checks.push({ name: 'Main guard', pass: hasMainGuard, weight: 5 });

    const hasClasses = /^class\s+\w+/m.test(content);
    checks.push({ name: 'Class definitions', pass: hasClasses, weight: 10 });

    const hasComments = /#\s*\w/.test(content);
    checks.push({ name: 'Comments', pass: hasComments, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Generic TypeScript File ─────────────────────────────────────────────────
function analyzeGenericTypeScript(content) {
    const checks = [];
    const details = [];

    const hasExports = /export\s+(function|const|class|type|interface|default)/g.test(content);
    checks.push({ name: 'Has exports', pass: hasExports, weight: 15 });

    const hasTypes = /interface\s+\w+|type\s+\w+\s*=/.test(content);
    checks.push({ name: 'Type definitions', pass: hasTypes, weight: 15 });

    const hasFunctions = (content.match(/(?:function|const\s+\w+\s*=\s*(?:\(|async))/g) || []).length;
    checks.push({ name: 'Functions', pass: hasFunctions > 0, weight: 15 });

    const hasErrorHandling = /try\s*{|catch\s*\(|\.catch\(/.test(content);
    checks.push({ name: 'Error handling', pass: hasErrorHandling, weight: 10 });

    const hasImports = /^import\s/m.test(content);
    checks.push({ name: 'Imports', pass: hasImports, weight: 10 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Substantial code', pass: lineCount > 10, weight: 10 });

    const hasComments = /\/\/|\/\*/.test(content);
    checks.push({ name: 'Comments', pass: hasComments, weight: 5 });

    const hasAsync = /async|await|Promise/.test(content);
    checks.push({ name: 'Async patterns', pass: hasAsync, weight: 5 });

    const hasNullSafety = /\?\.|!= null|!== null|!== undefined/.test(content);
    checks.push({ name: 'Null safety', pass: hasNullSafety, weight: 5 });

    const hasConstants = /const\s+[A-Z_]+\s*=/.test(content);
    checks.push({ name: 'Constants', pass: hasConstants, weight: 5 });

    checks.push({ name: 'Non-trivial', pass: lineCount > 3, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ── Mobile Files ────────────────────────────────────────────────────────────
function analyzeMobile(content, ext) {
    if (ext === '.json') return analyzeJsonConfig(content, path.basename(''));
    if (ext === '.tsx' || ext === '.ts') return analyzeComponent(content);
    return { percentage: 70, details: ['Mobile file'] };
}

// ── Build Config Files ──────────────────────────────────────────────────────
function analyzeBuildConfig(content) {
    const checks = [];

    const hasImport = /import|require|from/.test(content);
    checks.push({ name: 'Module imports', pass: hasImport, weight: 15 });

    const hasExport = /export\s+default|module\.exports/.test(content);
    checks.push({ name: 'Config exported', pass: hasExport, weight: 15 });

    const hasPlugins = /plugins|plugin/.test(content);
    checks.push({ name: 'Plugins configured', pass: hasPlugins, weight: 15 });

    const hasAlias = /alias|resolve/.test(content);
    checks.push({ name: 'Path aliases', pass: hasAlias, weight: 10 });

    const hasServer = /server|port|host/.test(content);
    checks.push({ name: 'Server config', pass: hasServer, weight: 10 });

    const hasBuild = /build|outDir|output/.test(content);
    checks.push({ name: 'Build config', pass: hasBuild, weight: 10 });

    const hasTest = /test|coverage|vitest/.test(content);
    checks.push({ name: 'Test config', pass: hasTest, weight: 10 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Has content', pass: lineCount > 3, weight: 10 });

    checks.push({ name: 'Non-trivial', pass: lineCount > 5, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details: [] };
}

// ── Type Definition Files ───────────────────────────────────────────────────
function analyzeTypes(content) {
    const checks = [];
    const details = [];

    const interfaceCount = (content.match(/interface\s+\w+/g) || []).length;
    const typeCount = (content.match(/type\s+\w+\s*=/g) || []).length;
    const total = interfaceCount + typeCount;
    checks.push({ name: 'Type definitions', pass: total > 0, weight: 25 });
    details.push(`Interfaces: ${interfaceCount}, Types: ${typeCount}`);

    const hasExports = /export\s+(interface|type)/g.test(content);
    checks.push({ name: 'Exported types', pass: hasExports, weight: 20 });

    const hasEnums = /enum\s+\w+/.test(content);
    checks.push({ name: 'Enums', pass: hasEnums || total > 2, weight: 10 });

    const hasOptional = /\?\s*:/.test(content);
    checks.push({ name: 'Optional properties', pass: hasOptional, weight: 10 });

    const hasArrayTypes = /\w+\[\]|Array</.test(content);
    checks.push({ name: 'Array/collection types', pass: hasArrayTypes, weight: 10 });

    const hasDocComments = /\/\*\*[\s\S]*?\*\//.test(content);
    checks.push({ name: 'JSDoc comments', pass: hasDocComments, weight: 10 });

    const lineCount = content.split('\n').length;
    checks.push({ name: 'Comprehensive types', pass: lineCount > 15, weight: 10 });

    checks.push({ name: 'Non-trivial', pass: total > 1, weight: 5 });

    return { percentage: calcWeightedPercentage(checks), details };
}

// ─── Utility Functions ──────────────────────────────────────────────────────

function calcWeightedPercentage(checks) {
    let totalWeight = 0;
    let passedWeight = 0;

    for (const check of checks) {
        totalWeight += check.weight;
        if (check.pass) passedWeight += check.weight;
    }

    return totalWeight > 0 ? Math.round((passedWeight / totalWeight) * 100) : 0;
}

function getObjectDepth(obj, depth = 0) {
    if (typeof obj !== 'object' || obj === null) return depth;
    const values = Object.values(obj);
    if (values.length === 0) return depth;
    return Math.max(...values.map(v => getObjectDepth(v, depth + 1)));
}

// ─── Main Analysis Entry Point ──────────────────────────────────────────────

function analyzeFile(filePath, workspaceRoot, testResults) {
    const domain = detectDomain(filePath, workspaceRoot);
    const basename = path.basename(filePath).toLowerCase();
    const ext = path.extname(filePath).toLowerCase();

    // Skip binary files and non-analyzable files
    const skipExts = ['.db', '.sqlite', '.pyc', '.pyo', '.whl', '.egg', '.ico', '.png', '.jpg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.lock'];
    if (skipExts.includes(ext)) {
        // For DB files, use file size as proxy
        if (ext === '.db' || ext === '.sqlite') {
            return analyzeDataFile(filePath, '');
        }
        return null;
    }

    // Skip __init__.py specially
    if (basename === '__init__.py') {
        const content = readFileContent(filePath);
        const result = analyzeInitFile(content);
        return {
            percentage: result.percentage,
            tooltip: result.details.join('\n'),
            domain: getDomainLabel(filePath, workspaceRoot)
        };
    }

    const content = readFileContent(filePath);
    if (!content && ext !== '.db') return null;

    let result;

    switch (domain) {
        case 'python-test':
            result = analyzePythonTest(content, testResults);
            break;
        case 'frontend-test':
            result = analyzeComponent(content); // Use component analysis for test files
            break;
        case 'test-config':
            result = analyzeCore(content);
            break;
        case 'api-route':
            result = analyzeApiRoute(content);
            break;
        case 'service':
            result = analyzeService(content);
            break;
        case 'model':
            result = analyzeModel(content);
            break;
        case 'core':
            result = analyzeCore(content);
            break;
        case 'repository':
            result = analyzeRepository(content);
            break;
        case 'background-job':
            result = analyzeGenericPython(content);
            break;
        case 'script':
            result = analyzeScript(content);
            break;
        case 'data':
            result = analyzeDataFile(filePath, content);
            break;
        case 'database':
            result = analyzeDatabase(content);
            break;
        case 'config':
            result = analyzeCore(content);
            break;
        case 'main-entry':
            result = analyzeCore(content);
            break;
        case 'ai-matcher':
        case 'ai-engine':
        case 'ai-search':
            result = analyzeAIModule(content);
            break;
        case 'component':
            result = analyzeComponent(content);
            break;
        case 'hook':
            result = analyzeHook(content);
            break;
        case 'frontend-lib':
            result = analyzeFrontendLib(content);
            break;
        case 'types':
            result = analyzeTypes(content);
            break;
        case 'app-entry':
            result = analyzeComponent(content);
            break;
        case 'stylesheet':
            result = analyzeStylesheet(content);
            break;
        case 'package-config':
        case 'ts-config':
        case 'json-config':
            result = analyzeJsonConfig(content, basename);
            break;
        case 'build-config':
            result = analyzeBuildConfig(content);
            break;
        case 'env-config':
            result = analyzeEnvConfig(content);
            break;
        case 'python-deps':
            result = analyzePythonDeps(content);
            break;
        case 'ci-cd':
            result = analyzeCICD(content);
            break;
        case 'docker':
            result = analyzeDocker(content);
            break;
        case 'docker-compose':
            result = analyzeYamlConfig(content);
            break;
        case 'deploy-config':
            result = analyzeDeployConfig(content, basename);
            break;
        case 'documentation':
            result = analyzeDocumentation(content);
            break;
        case 'mobile':
            result = analyzeMobile(content, ext);
            break;
        case 'python-generic':
            result = analyzeGenericPython(content);
            break;
        case 'typescript-generic':
            result = analyzeGenericTypeScript(content);
            break;
        case 'yaml-config':
            result = analyzeYamlConfig(content);
            break;
        default:
            // For unknown files, basic content analysis
            const lineCount = content.split('\n').length;
            result = {
                percentage: lineCount > 10 ? 70 : (lineCount > 3 ? 55 : 35),
                details: [`Lines: ${lineCount}`]
            };
    }

    if (!result) return null;

    const domainLabel = getDomainLabel(filePath, workspaceRoot);
    const detailsText = result.details?.length > 0 ? '\n' + result.details.join('\n') : '';

    return {
        percentage: Math.min(100, Math.max(0, result.percentage)),
        tooltip: `${domainLabel}: ${result.percentage}%${detailsText}`,
        domain: domainLabel
    };
}

function computeFolderPercentage(folderPath, fileResults) {
    // This is handled in the extension.js now
    return null;
}

module.exports = { analyzeFile, computeFolderPercentage, getDomainLabel, detectDomain };
