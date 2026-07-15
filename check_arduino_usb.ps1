 param()

$logitechPattern = 'VID_046D&PID_C07D'
$defaultPattern = 'VID_2341&PID_8036'
$devices = Get-CimInstance Win32_PnPEntity | Where-Object {
    $hardwareIds = ($_.HardwareID -join ';')
    $hardwareIds -match $logitechPattern -or $hardwareIds -match $defaultPattern
}

Write-Output ('=' * 60)
Write-Output 'Arduino USB Descriptor Check'
Write-Output ('=' * 60)

if (-not $devices) {
    Write-Output 'No matching Arduino USB device found.'
    exit 1
}

$foundLogitech = $false
foreach ($device in $devices) {
    $hardwareIds = ($device.HardwareID -join ';')
    $isLogitech = $hardwareIds -match $logitechPattern
    if ($isLogitech) {
        $foundLogitech = $true
    }

    Write-Output "Device Name: $($device.Name)"
    Write-Output "Status: $($device.Status)"
    Write-Output "Device ID: $($device.PNPDeviceID)"
    Write-Output "Logitech descriptor: $isLogitech"
    Write-Output ''
}

if ($foundLogitech) {
    Write-Output 'SUCCESS: VID_046D and PID_C07D detected.'
    exit 0
}

Write-Output 'Logitech VID/PID not detected; the device may still use the default Arduino descriptor.'
exit 1
