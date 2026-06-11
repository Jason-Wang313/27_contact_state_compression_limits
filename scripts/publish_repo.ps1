$ErrorActionPreference = "Continue"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DataDir = Join-Path $Root "data"
$StatusPath = Join-Path $DataDir "git_push_status.json"
$RepoName = "27_contact_state_compression_limits"

if (!(Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}

$status = [ordered]@{
    status = "started"
    repo_name = $RepoName
    commands = @()
}

function Run-Cmd {
    param(
        [string]$Name,
        [string]$Exe,
        [string[]]$ArgList
    )
    Push-Location $Root
    try {
        $output = & $Exe @ArgList 2>&1
        $code = $LASTEXITCODE
        if ($null -eq $code) { $code = 0 }
    } catch {
        $output = $_.Exception.Message
        $code = 1
    } finally {
        Pop-Location
    }
    $status.commands += [ordered]@{
        name = $Name
        exe = $Exe
        args = ($ArgList -join " ")
        exit_code = $code
        output = (($output | Out-String).Trim())
    }
    return @{ code = $code; output = (($output | Out-String).Trim()) }
}

$email = Run-Cmd -Name "git_config_email" -Exe "git" -ArgList @("config", "user.email")
if ($email.code -ne 0 -or [string]::IsNullOrWhiteSpace($email.output)) {
    Run-Cmd -Name "git_config_email_set" -Exe "git" -ArgList @("config", "user.email", "paper-agent@example.invalid") | Out-Null
}
$name = Run-Cmd -Name "git_config_name" -Exe "git" -ArgList @("config", "user.name")
if ($name.code -ne 0 -or [string]::IsNullOrWhiteSpace($name.output)) {
    Run-Cmd -Name "git_config_name_set" -Exe "git" -ArgList @("config", "user.name", "Paper Agent") | Out-Null
}

Run-Cmd -Name "git_add" -Exe "git" -ArgList @("add", "-A") | Out-Null
$commit = Run-Cmd -Name "git_commit" -Exe "git" -ArgList @("commit", "-m", "Add contact state compression limits paper package")
if ($commit.code -ne 0) {
    $short = Run-Cmd -Name "git_status_after_commit" -Exe "git" -ArgList @("status", "--short")
    if (![string]::IsNullOrWhiteSpace($short.output)) {
        $status.status = "commit_failed"
        $status.error = $commit.output
        $status | ConvertTo-Json -Depth 6 | Set-Content -Path $StatusPath -Encoding UTF8
        exit 0
    }
}

Run-Cmd -Name "git_branch_main" -Exe "git" -ArgList @("branch", "-M", "main") | Out-Null

$auth = Run-Cmd -Name "gh_auth_status" -Exe "gh" -ArgList @("auth", "status")
if ($auth.code -ne 0) {
    $status.status = "gh_auth_failed"
    $status.error = $auth.output
    $status | ConvertTo-Json -Depth 6 | Set-Content -Path $StatusPath -Encoding UTF8
    exit 0
}

$owner = Run-Cmd -Name "gh_user" -Exe "gh" -ArgList @("api", "user", "--jq", ".login")
if ($owner.code -ne 0 -or [string]::IsNullOrWhiteSpace($owner.output)) {
    $status.status = "gh_user_failed"
    $status.error = $owner.output
    $status | ConvertTo-Json -Depth 6 | Set-Content -Path $StatusPath -Encoding UTF8
    exit 0
}
$OwnerName = $owner.output.Trim()
$RepoFull = "$OwnerName/$RepoName"
$GithubUrl = "https://github.com/$RepoFull"
$RemoteUrl = "$GithubUrl.git"
$status.github_url = $GithubUrl

$view = Run-Cmd -Name "gh_repo_view" -Exe "gh" -ArgList @("repo", "view", $RepoFull, "--json", "url", "--jq", ".url")
if ($view.code -ne 0) {
    $create = Run-Cmd -Name "gh_repo_create" -Exe "gh" -ArgList @("repo", "create", $RepoName, "--public", "--description", "Paper 27: Contact State Compression Limits")
    if ($create.code -ne 0) {
        $status.status = "repo_create_failed"
        $status.error = $create.output
        $status | ConvertTo-Json -Depth 6 | Set-Content -Path $StatusPath -Encoding UTF8
        exit 0
    }
} else {
    Run-Cmd -Name "gh_repo_public" -Exe "gh" -ArgList @("repo", "edit", $RepoFull, "--visibility", "public", "--accept-visibility-change-consequences") | Out-Null
}

$remote = Run-Cmd -Name "git_remote_get" -Exe "git" -ArgList @("remote", "get-url", "origin")
if ($remote.code -eq 0) {
    Run-Cmd -Name "git_remote_set" -Exe "git" -ArgList @("remote", "set-url", "origin", $RemoteUrl) | Out-Null
} else {
    Run-Cmd -Name "git_remote_add" -Exe "git" -ArgList @("remote", "add", "origin", $RemoteUrl) | Out-Null
}

$push = Run-Cmd -Name "git_push" -Exe "git" -ArgList @("push", "-u", "origin", "main")
if ($push.code -eq 0) {
    $status.status = "complete"
    $status.message = "Repository pushed"
} else {
    $status.status = "push_failed"
    $status.error = $push.output
}

$status | ConvertTo-Json -Depth 6 | Set-Content -Path $StatusPath -Encoding UTF8
exit 0
