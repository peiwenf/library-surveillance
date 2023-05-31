# Libraries
library(rvest)
library(stringr)
library(tidyverse)
library(RCurl)
library(plyr)
library(rlang)
library(writexl)
library(magrittr)
library(stringi)

# get the library links for each state
nation_page <- read_html("https://librarytechnology.org/libraries/uspublic/")
nation_links <- nation_page %>% html_nodes("tr > td > a") %>% html_attr("href")
states_links <- nation_links[!grepl("pl\\?City=", nation_links)]
# get the states names
states <- character(length(states_links))
for (i in seq_along(states_links)) {
  states[i] <- str_extract(states_links[i], "(?<=pl\\?State=).*")
}

total_lib_data_1 <- data.frame()
# get the link for each library
for (s in 41:length(states_links)){
  page_url <- URLencode(states_links[s])
  list_page <- read_html(page_url)
  lib_content <- list_page %>% html_nodes("#pagebodycontainer > div > p > a") %>% html_attr("href")
  lib_links <- list()
  # Iterate over the data and filter the rows
  for (k in 1:(length(lib_content)-1)) {
    if (grepl("^/library/\\d+$", lib_content[k]) && (grepl("http://", lib_content[k+1]) || grepl("https://", lib_content[k+1]))) {
      lib_links[[length(lib_links)+1]] <- lib_content[k]
    }
  }
  
  # the final data 
  lib_data <- data.frame()
  # get into each library page
  for(i in 1:length(lib_links)){
    print(i)
    # get the content
    url <- paste("https://librarytechnology.org",lib_links[i],sep = "")
    webpage <- read_html(url)
    # get links and basic info
    library_element = webpage %>%  html_node(xpath = "//*[contains(text(), 'Library Web Site')]")
    library_link <- ifelse(!is.null(library_element), html_attr(library_element, "href"), NA)
    catalog_element = webpage %>%  html_node(xpath = "//*[contains(text(), 'Online Catalog')]")
    catalog_link <- ifelse(!is.null(catalog_element), html_attr(catalog_element, "href"), NA)
    lib_info <- data.frame(Library = html_node(webpage, 
                                               "#fullsinglecolumn > h2 > span") %>% 
                             html_text() %>% str_remove_all("\r\n"), 
                           Location = html_node(webpage, 
                                                "#fullsinglecolumn > h3") %>% 
                             html_text(), 
                           State = states[s],
                           Homepage = library_link,
                           Catalog = catalog_link)
    # get the vendor info
    table <- html_node(webpage, xpath = "//table[.//th[contains(text(), 'Technology Profile')]]")
    rows <- html_nodes(table, "tr:nth-child(n+3)") # don't grab td
    header_values_raw <- html_text(html_nodes(rows, "th"))
    header_values <- header_values_raw %>% make.unique(sep = "_") %>% rep(each = 2)
    if (length(header_values) == 0) {
      lib_data <- rbind.fill(lib_data, lib_info)
    }else{
      column_names <- paste(header_values, c("Name", "Year"), sep = " ")
      vendor_info <- data.frame(matrix(ncol = length(column_names), nrow = 0))
      colnames(vendor_info) <- column_names
      value_list <- list()
      for (i in 1:(length(rows)-sum(is.na(html_node(rows, "th"))))) {
        tds <- html_nodes(rows[i], "td")
        
        column_values <- html_text(tds[1:2])
        value_list <- c(value_list, column_values[1] %>% str_remove_all("\r\n"))
        value_list <- c(value_list, column_values[2] %>% str_remove_all("\r\n"))
      }
      for (i in 1:length(value_list)) {
        vendor_info[1, i] <- value_list[[i]]
      }
      lib_page <- bind_cols(lib_info, vendor_info)
      lib_data <- rbind.fill(lib_data, lib_page)
    }
  }
  total_lib_data_1 <- rbind.fill(total_lib_data_1, lib_data)
}

total_lib_data_2 <- rbind.fill(total_lib_data, total_lib_data_1)
