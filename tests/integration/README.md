# Integration Tests

This directory contains integration tests that use **real JV-Link API** to fetch actual horse racing data from JRA-VAN DataLab.

## Requirements

1. **JV-Link Installation**
   - JV-Link must be installed on Windows
   - COM object `JVDTLab.JVLink` must be available

2. **JRA-VAN Subscription**
   - Active JRA-VAN DataLab subscription required (月額2,090円)
   - Valid service key needed

3. **Environment Setup**
   - Set `JVLINK_SERVICE_KEY` environment variable with your service key

## Setup

### Windows Command Prompt
```cmd
set JVLINK_SERVICE_KEY=YOUR_SERVICE_KEY_HERE
```

### Windows PowerShell
```powershell
$env:JVLINK_SERVICE_KEY="YOUR_SERVICE_KEY_HERE"
```

### Git Bash / MSYS2
```bash
export JVLINK_SERVICE_KEY="YOUR_SERVICE_KEY_HERE"
```

### Permanent Setup (Windows)
1. Open "Environment Variables" in System Properties
2. Add new User Variable:
   - Name: `JVLINK_SERVICE_KEY`
   - Value: Your JV-Link service key

## Running Tests

### Run all integration tests
```bash
pytest tests/integration/ -v -s
```

### Run specific test
```bash
pytest tests/integration/test_jvlink_real.py::TestJVLinkRealDataFetching::test_full_workflow_with_real_data -v -s
```

### Run without service key (tests will be skipped)
```bash
pytest tests/integration/test_jvlink_real.py -v
```

## Test Coverage

### test_jvlink_real.py

**TestJVLinkRealDataFetching**
- `test_jvlink_connection` - Verifies JV-Link initialization
- `test_fetch_small_data_sample` - Fetches small sample of real data
- `test_full_workflow_with_real_data` - Complete workflow: Fetch → Parse → Import → Verify
- `test_parser_with_real_data_formats` - Verifies parser field coverage

**TestJVLinkErrorHandling**
- `test_invalid_date_range` - Tests error handling for invalid dates
- `test_future_date_handling` - Tests fetching future dates (should return no data)

## What Gets Tested

1. **JV-Link Connection**: Verify COM object initialization
2. **Data Fetching**: Fetch real race data from JRA-VAN
3. **Data Parsing**: Parse fixed-length JV-Data format
4. **Database Import**: Import parsed data to SQLite
5. **Data Verification**: Verify imported data integrity
6. **Error Handling**: Test invalid inputs and edge cases

## Expected Output

When running tests with a valid service key, you should see:

```
=== Fetching RACE data for 20241107 ===

--- Fetcher Statistics ---
Records fetched: 100
Records parsed:  100
Records failed:  0

--- Record Types Found ---
HR: 20 records
RA: 15 records
SE: 65 records

--- Sample Record (Type: RA) ---
headRecordSpec: RA
headDataKubun: 1
headMakeDate: 20241107
idYear: 2024
idMonthDay: 1107
idJyoCD: 05
idKaiji: 05
idNichiji: 02
idRaceNum: 01
RaceName: 新馬
... (truncated)

=== Full Workflow Integration Test ===
Date range: 20241107 - 20241107

Processing data...

--- Processing Statistics ---
Records fetched:  150
Records parsed:   150
Records imported: 150
Records failed:   0
Batches processed: 3

--- Database Verification ---
NL_RA_RACE records: 15
NL_SE_RACE_UMA records: 120
NL_HR_PAY records: 15

--- Sample Race Record ---
Year: 2024
Race Number: 01
Race Name: 新馬
Distance: 1200
Track Code: 05

Total records in DB: 150

✓ Full workflow test PASSED
```

## Notes

- Tests use data from 7 days ago to ensure availability
- Tests fetch limited records (50-100) for quick execution
- All tests skip gracefully if `JVLINK_SERVICE_KEY` is not set
- Database operations use temporary SQLite file (auto-cleaned)
- Tests verify both successful operations and error handling

## Troubleshooting

### "JVLINK_SERVICE_KEY not set - skipping integration tests"
- Set the environment variable as described above

### "JV-Link initialization failed"
- Verify JV-Link is installed
- Check Windows Registry for JV-Link COM registration
- Run: `python -c "import win32com.client; print(win32com.client.Dispatch('JVDTLab.JVLink'))"`

### "No records were fetched"
- Check internet connection
- Verify JRA-VAN subscription is active
- Try different date range (data may not be available for all dates)
- Check JV-Link service status

### "Failed to import data"
- Check database permissions
- Verify disk space available
- Check temp directory write access
