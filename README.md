# IPv4Info Scraper

Get the IP blocks and their domains from a company name by scrapping IPv4info

## Usage

```
python3 main.py [-c COMPANIES_FILE] [-C COMPANIES_LIST] [-f COUNTRY_FILTER] [-o OUTPUT_FILE] [-d]
```

The parameters are:

	* -C: Comma-separated list of companies. Example: -C google,yahoo,youtube
	
	* -c: File with list of companies

	* -f: Country codes to filter ranges. Example to grab ranges from Spain+United States: -f ES,US
	
	* -o: Output file to store JSON. Default: output.txt

	* -d: Debug mode to check urls that are scrapped. Default: False


### Option -C (comma-separated list)

![example sprayer](https://i.imgur.com/6meZjSQ.png)


### Option -c (list from file)

![example sprayer](https://i.imgur.com/B5ysIMV.png)
