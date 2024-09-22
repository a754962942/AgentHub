from tabulate import tabulate

# GDP data for China from 2010 to 2023 in billions of US dollars
gdp_data = [
    ["2010", 6087.16],
    ["2011", 7551.50],
    ["2012", 8532.23],
    ["2013", 9570.40],
    ["2014", 10475.68],
    ["2015", 11015.54],
    ["2016", 11233.27],
    ["2017", 12143.49],
    ["2018", 13608.15],
    ["2019", 14279.94],
    ["2020", 14722.73],
    ["2021", 17734.06],
    ["2022", 17963.17],
    ["2023", 17794.78]
]

# Generate the table
table = tabulate(gdp_data, headers=["Year", "GDP (in billions of USD)"], tablefmt="grid")

# Print the table
print(table)