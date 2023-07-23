Add-Type -AssemblyName System.Windows.Forms

$filesToProcess = @(Get-ChildItem -Path $PSScriptRoot -Filter *img)

if ($filesToProcess.Count -eq 0) {
    Write-Host "no files in current directory $PSScriptRoot"
    $foldername = New-Object System.Windows.Forms.FolderBrowserDialog
    $foldername.Description = "Select folder containing one or more miyoo...fw.img"

    if ($foldername.ShowDialog() -eq "OK") {
        $filesToProcess = @(Get-ChildItem -Path $foldername.SelectedPath -Filter *img)
        if ($filesToProcess.Count -eq 0) {
            exit
        }
    }
    else {
        exit
    }
    
}

foreach ($file in $filesToProcess) {
    $folder = Join-Path ($file.FullName | Split-Path -Parent) "extracted"
    New-Item -Type directory -Path $folder -ErrorAction SilentlyContinue
    $leaf = $file.Name
    $script = ""
    
    foreach ($line in Get-Content $file.FullName) {
        $script += "$line`n"
        if ($line -match "%") {
            break
        }
    }
    
    $partitions = @()
    $offsets = @()
    $offsetsdecimal = @()
    $sizes = @()
    $sizesdecimal = @()
    $script.Split("#") | ForEach-Object {
        $_.Split("`n") | ForEach-Object {
            
            if ($_ -match "File Partition:" -and $_ -notmatch "set_config") {
                $partitions += $_.Split(" ")[-1]
            }
            if ($_ -match "fatload mmc") {
                $sizes += $_.Split(" ")[-2]
                $sizesdecimal += [Int32]$_.Split(" ")[-2]
                $offsets += $_.Split(" ")[-1]
                $offsetsdecimal += [Int32]$_.Split(" ")[-1]
            }
        }
    }
    
    $rawfile = [System.IO.File]::ReadAllBytes($file.FullName)
    
    for ($i = 0; $i -lt $partitions.Count; $i++) {
        Write-Host "Processing partition $($partitions[$i]) offset $($offsets[$i]) size $($sizes[$i])"
        $outputBytes = $rawfile[$offsetsdecimal[$i]..($offsetsdecimal[$i] + $sizesdecimal[$i] - 1)]
        $outputPath = (Join-Path $folder "$($leaf.Split("_")[0])_$($partitions[$i])")
        [System.IO.File]::WriteAllBytes($outputPath, $outputBytes)
    }
}
