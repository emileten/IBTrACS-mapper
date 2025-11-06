function MonthSelector({ value, onChange, onPlot }) {
  // Parse current value (format: YYYY-MM)
  const [year, month] = value.split('-')

  // Generate years from 1950 to current year + 1
  const currentYear = new Date().getFullYear()
  const years = []
  for (let y = 1950; y <= currentYear + 1; y++) {
    years.push(y)
  }

  // Month names
  const months = [
    { value: '01', label: 'January' },
    { value: '02', label: 'February' },
    { value: '03', label: 'March' },
    { value: '04', label: 'April' },
    { value: '05', label: 'May' },
    { value: '06', label: 'June' },
    { value: '07', label: 'July' },
    { value: '08', label: 'August' },
    { value: '09', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' },
  ]

  const handleYearChange = (e) => {
    const newYear = e.target.value
    onChange(`${newYear}-${month}`)
  }

  const handleMonthChange = (e) => {
    const newMonth = e.target.value
    onChange(`${year}-${newMonth}`)
  }

  return (
    <div className="month-selector">
      <label>Select Month:</label>
      <div className="month-selector-controls">
        <select
          id="year-select"
          value={year}
          onChange={handleYearChange}
          className="month-selector-select"
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
        <select
          id="month-select"
          value={month}
          onChange={handleMonthChange}
          className="month-selector-select"
        >
          {months.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
        <button
          onClick={onPlot}
          className="month-selector-button"
          type="button"
        >
          Plot
        </button>
      </div>
    </div>
  )
}

export default MonthSelector

