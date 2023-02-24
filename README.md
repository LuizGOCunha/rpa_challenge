A automation process that contains a class called InfoGetter.
This class is responsible for returning data about new york times articles based on three basics variables:
- query: string to be searched in the site
- section: section to be used to filter searches
- months: How many months old are articles allowed to be

Based on that it createds a dict from each article that can be acessed using the attribute .parsed_info

PROBLEMS: 
- New York Times create sections dynamically, which means my dictionary approached has been made invalid. Possible solution: Make the system separate sections by order, instead of name.