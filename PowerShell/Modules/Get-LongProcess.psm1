


function Get-LongProcess {

    param(
        [Parameter(ValueFromPipeline)]
        $Process
    )

    process {
        if ($Process.CPU -gt 50) {
            Write-Output "$($Process.Name) uses $($Process.CPU) CPU."
        }
    }
}

Export-ModuleMember -Function Get-LongProcess
