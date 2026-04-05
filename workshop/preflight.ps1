$ErrorActionPreference = 'Stop'

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Failures = 0
$Warnings = 0
$RequiredNodeMajor = 22
$RequiredNpmMajor = 9
$RequiredPythonVersion = [Version]'3.11.0'

function Write-Ok($Message) {
    Write-Host "[ok] $Message"
}

function Write-Warn($Message) {
    Write-Host "[warn] $Message"
    $script:Warnings++
}

function Write-Fail($Message) {
    Write-Host "[fail] $Message"
    $script:Failures++
}

function Test-Command($Name, $Label) {
    $Command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $Command) {
        Write-Ok "$Label: $($Command.Source)"
    } else {
        Write-Fail "$Label not found"
    }
}

function Test-OptionalCommand($Name, $Label) {
    $Command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $Command) {
        try {
            $VersionLine = (& $Name --version 2>$null | Select-Object -First 1)
            if ($VersionLine) {
                Write-Ok "$Label: $VersionLine"
            } else {
                Write-Ok "$Label is installed"
            }
        } catch {
            Write-Ok "$Label is installed"
        }
    } else {
        Write-Warn "$Label not found on host (this is fine if you will use the devcontainer)"
    }
}

function Test-DockerCompose {
    try {
        $VersionLine = (docker compose version 2>$null | Select-Object -First 1)
        if ($VersionLine) {
            Write-Ok "Docker Compose plugin: $VersionLine"
        } else {
            Write-Fail "Docker Compose plugin is not available. Install or enable 'docker compose'."
        }
    } catch {
        Write-Fail "Docker Compose plugin is not available. Install or enable 'docker compose'."
    }
}

function Test-WslForDevcontainers {
    $IsWindowsHost = $false
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        $IsWindowsHost = $IsWindows
    } elseif ($env:OS -eq 'Windows_NT') {
        $IsWindowsHost = $true
    }

    if (-not $IsWindowsHost) {
        return
    }

    $WslCommand = Get-Command wsl -ErrorAction SilentlyContinue
    if ($null -eq $WslCommand) {
        Write-Fail 'WSL is not installed. For Windows devcontainers in this workshop, install WSL 2 and enable the Docker Desktop WSL 2 backend.'
        return
    }

    try {
        $StatusOutput = (wsl --status 2>&1 | Select-Object -First 5)
        if ($LASTEXITCODE -eq 0) {
            Write-Ok 'WSL is available for Windows devcontainers'
        } else {
            Write-Fail 'WSL is not configured correctly. For Windows devcontainers in this workshop, install WSL 2 and enable the Docker Desktop WSL 2 backend.'
        }
    } catch {
        Write-Fail 'WSL is not configured correctly. For Windows devcontainers in this workshop, install WSL 2 and enable the Docker Desktop WSL 2 backend.'
    }
}

function Test-NodeVersion() {
    $Command = Get-Command node -ErrorAction SilentlyContinue
    if ($null -eq $Command) {
        Write-Warn 'Node.js not found on host. This is fine for the devcontainer path but required for local setup.'
        return
    }

    try {
        $VersionText = (& node --version 2>$null | Select-Object -First 1)
        if ($VersionText -match '^v(?<major>\d+)') {
            $Major = [int]$Matches['major']
            if ($Major -lt $RequiredNodeMajor) {
                Write-Warn "Node.js host version is $VersionText. This project pins Node $RequiredNodeMajor in .nvmrc and the devcontainer."
            } else {
                Write-Ok "Node.js version is suitable for local setup: $VersionText"
            }
        }
    } catch {
        return
    }
}

function Test-NpmVersion() {
    $Command = Get-Command npm -ErrorAction SilentlyContinue
    if ($null -eq $Command) {
        Write-Warn 'npm not found on host. This is fine for the devcontainer path but required for local setup.'
        return
    }

    try {
        $VersionText = (& npm --version 2>$null | Select-Object -First 1)
        if ($VersionText -match '^(?<major>\d+)') {
            $Major = [int]$Matches['major']
            if ($Major -lt $RequiredNpmMajor) {
                Write-Warn "npm host version is $VersionText. Use npm $RequiredNpmMajor+ for local setup."
            } else {
                Write-Ok "npm version is suitable for local setup: $VersionText"
            }
        }
    } catch {
        return
    }
}

function Get-PythonCommand {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $Python) {
        return @{ Name = 'python'; Display = $Python.Source }
    }

    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $PyLauncher) {
        return @{ Name = 'py'; Display = $PyLauncher.Source }
    }

    return $null
}

function Test-PythonVersion {
    $PythonInfo = Get-PythonCommand
    if ($null -eq $PythonInfo) {
        Write-Warn 'Python 3.11+ not found on host. This is fine for the devcontainer path but required for local setup.'
        return
    }

    try {
        $VersionText = (& $PythonInfo.Name --version 2>&1 | Select-Object -First 1)
        if ($VersionText -match 'Python (?<version>\d+\.\d+(\.\d+)?)') {
            $Version = [Version]$Matches['version']
            if ($Version -lt $RequiredPythonVersion) {
                Write-Warn "Python host version is $Version via $($PythonInfo.Name). Use Python $RequiredPythonVersion or newer for local setup."
            } else {
                Write-Ok "Python version is suitable for local setup: $Version via $($PythonInfo.Name)"
            }
        }
    } catch {
        return
    }
}

function Test-Uv {
    $Command = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -eq $Command) {
        Write-Warn 'uv not found on host. This is fine for the devcontainer path but required for local setup.'
        return
    }

    try {
        $VersionLine = (& uv --version 2>$null | Select-Object -First 1)
        if ($VersionLine) {
            Write-Ok "uv: $VersionLine"
        } else {
            Write-Ok 'uv is installed'
        }
    } catch {
        Write-Ok 'uv is installed'
    }
}

Write-Host "Workshop preflight for $ProjectDir"
Write-Host ""

Write-Host 'Recommended devcontainer host requirements:'
Test-Command git "Git"
Test-Command docker "Docker CLI"
Test-WslForDevcontainers

try {
    docker info | Out-Null
    Write-Ok "Docker daemon is running"
} catch {
    Write-Fail "Docker daemon is not reachable. Start Docker Desktop or Docker Engine."
}
Test-DockerCompose

Write-Host ''
Write-Host 'Optional local setup checks:'
Test-NodeVersion
Test-NpmVersion
Test-PythonVersion
Test-Uv

$EnvPath = Join-Path $ProjectDir '.env'
if (Test-Path $EnvPath) {
    Write-Ok '.env file exists'
    $EnvContents = Get-Content $EnvPath -Raw
    if ($EnvContents -match '(?m)^OPENAI_API_KEY=.+$') {
        Write-Ok 'OPENAI_API_KEY is set in .env'
    } else {
        Write-Warn 'OPENAI_API_KEY is missing in .env'
    }
} else {
    Write-Warn '.env file missing. Run .\workshop\init_env.ps1 first.'
}

if (Get-Command code -ErrorAction SilentlyContinue) {
    Write-Ok 'VS Code command available'
} elseif (Get-Command cursor -ErrorAction SilentlyContinue) {
    Write-Ok 'Cursor command available'
} else {
    Write-Warn "No 'code' or 'cursor' command found. This is fine if you open the IDE manually."
}

Write-Host ""
if ($Failures -eq 0) {
    Write-Host "Preflight passed with $Warnings warning(s)."
    Write-Host 'Next steps:'
    Write-Host '  1. For the recommended path, open the repo in your editor and reopen in the devcontainer.'
    Write-Host "  2. For local setup, make sure Node $RequiredNodeMajor, npm $RequiredNpmMajor+, Python $RequiredPythonVersion+, and uv are installed."
    Write-Host '  3. Run .\workshop\init_env.ps1 and add OPENAI_API_KEY to .env if needed.'
    Write-Host '  4. Run npm run start, then .\workshop\healthcheck.ps1.'
    exit 0
}

Write-Host "Preflight failed with $Failures issue(s) and $Warnings warning(s)."
exit 1
