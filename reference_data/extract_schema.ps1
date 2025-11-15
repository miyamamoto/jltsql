# Extract schema from Access database
param(
    [string]$MdbPath = "C:\Users\mitsu\jltsql\reference_data\Data.mdb",
    [string]$OutputPath = "C:\Users\mitsu\jltsql\reference_data\schema_info.txt"
)

try {
    # Create ADOX connection to Access database
    $adox = New-Object -ComObject ADOX.Catalog
    $connectionString = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=$MdbPath"

    try {
        $adox.ActiveConnection = $connectionString
    } catch {
        # Try ACE driver if Jet fails
        $connectionString = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=$MdbPath"
        $adox.ActiveConnection = $connectionString
    }

    $output = @()
    $output += "=" * 80
    $output += "JRA-VAN Standard Database Schema (Data.mdb)"
    $output += "=" * 80
    $output += ""

    # Get all tables
    $tables = $adox.Tables
    $output += "Total Tables: $($tables.Count)"
    $output += ""

    # Extract schema for each table
    foreach ($table in $tables) {
        # Skip system tables
        if ($table.Type -eq "TABLE") {
            $tableName = $table.Name
            $output += "-" * 80
            $output += "Table: $tableName"
            $output += "-" * 80

            $columns = $table.Columns
            $output += "Columns: $($columns.Count)"
            $output += ""

            # Column details
            $output += "{0,-5} {1,-40} {2,-20} {3,-10} {4}" -f "No", "Column Name", "Data Type", "Size", "Attributes"
            $output += "{0,-5} {1,-40} {2,-20} {3,-10} {4}" -f "---", "-----------", "---------", "----", "----------"

            $colNum = 1
            foreach ($column in $columns) {
                $colName = $column.Name
                $dataType = $column.Type
                $size = $column.DefinedSize

                # Convert ADO type number to readable name
                $typeName = switch ($dataType) {
                    2 { "SmallInt" }
                    3 { "Integer" }
                    4 { "Single" }
                    5 { "Double" }
                    6 { "Currency" }
                    7 { "Date" }
                    11 { "Boolean" }
                    17 { "Byte" }
                    20 { "BigInt" }
                    72 { "GUID" }
                    128 { "Binary" }
                    129 { "Char" }
                    130 { "VarChar" }
                    200 { "VarChar" }
                    201 { "LongText" }
                    202 { "VarWChar" }
                    203 { "LongText" }
                    204 { "Binary" }
                    205 { "Image" }
                    default { "Type_$dataType" }
                }

                $attributes = @()
                if ($column.Attributes -band 1) { $attributes += "Fixed" }
                if ($column.Attributes -band 2) { $attributes += "Nullable" }
                if ($column.Attributes -band 16) { $attributes += "AutoIncrement" }

                $attrStr = $attributes -join ", "

                $output += "{0,-5} {1,-40} {2,-20} {3,-10} {4}" -f $colNum, $colName, $typeName, $size, $attrStr
                $colNum++
            }

            $output += ""
        }
    }

    # Save to file
    $output | Out-File -FilePath $OutputPath -Encoding UTF8

    Write-Host "Schema extraction completed successfully!"
    Write-Host "Output saved to: $OutputPath"
    Write-Host "Total tables processed: $($tables.Count)"

    # Cleanup
    $adox.ActiveConnection = $null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($adox) | Out-Null

} catch {
    Write-Host "Error: $_"
    Write-Host "Exception: $($_.Exception.Message)"
    exit 1
}
