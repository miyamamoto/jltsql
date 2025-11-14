# JV-Link Service Key Setup Script
# Registers service key to Windows Registry

$serviceKey = "1UJC-VRFM-24YD-K2W4-4"

# Try both possible registry paths
$regPaths = @(
    "HKLM:\SOFTWARE\JRA-VAN\JV-Link",
    "HKLM:\SOFTWARE\WOW6432Node\JRA-VAN\JV-Link",
    "HKCU:\SOFTWARE\JRA-VAN\JV-Link"
)

foreach ($path in $regPaths) {
    try {
        if (!(Test-Path $path)) {
            New-Item -Path $path -Force | Out-Null
            Write-Host "Created registry path: $path"
        }

        Set-ItemProperty -Path $path -Name "ServiceKey" -Value $serviceKey -Type String
        Write-Host "Set service key at: $path"
    }
    catch {
        Write-Host "Could not set at $path : $_"
    }
}

Write-Host "`nService key setup complete!"
Write-Host "Please restart JVLinkAgent service or reboot Windows."
