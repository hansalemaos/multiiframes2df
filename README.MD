# scrapes a website (Selenium, SeleniumBase, undetected chromedriver ...) with iframes and returns a DataFrame

## Tested against Windows / Python 3.11 / Anaconda

## pip install multiiframes2df

```
Scrapes data using the provided driver and processes it to return a DataFrame
which includes each element and its children.

Args:
	driver: The driver used to scrape the data.
	filter_function: A function to filter the scraped data (default is None).
	chunks: The number of chunks to divide the data into for processing (default is 1).
	processes: The number of processes to use for parallel processing (default is 4).
	print_stdout: Boolean indicating whether to print stdout (default is False).
	print_stderr: Boolean indicating whether to print stderr (default is True).

Returns:
	pandas DataFrame: The processed and filtered data.

Example:
	from PrettyColorPrinter import add_printer  # optional
	from seleniumbase import Driver
	from multiiframes2df import fast_scrape

	add_printer(1)
	driver = Driver(uc=True, undetected=True)
	driver.get(r"https://testpages.herokuapp.com/styled/iframes-test.html")
	df = fast_scrape(
		driver=driver,
		filter_function=None,
		chunks=1,
		processes=4,
		print_stdout=False,
		print_stderr=True,
	)
	for name, group in df.groupby("aa_groupnumber"):
		print(name, group)


	df2 = fast_scrape(
		driver=driver,
		filter_function=lambda x: "List" in x and "<html>" not in x and "<body>" not in x,
		chunks=1,
		processes=4,
		print_stdout=False,
		print_stderr=True,
	)
	for name, group in df2.groupby("aa_groupnumber"):
		print(name, group)
		
```
