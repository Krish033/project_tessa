

function ReadFile {

    param($Path)

    process {
        try {
            Get-Content $Path -ErrorAction Stop
        }
        catch {
            Write-Output $_.Exception.Message
        }
        finally {
            Write-Output "Finished reading"
        }
    }
}

Export-ModuleMember -Function ReadFile