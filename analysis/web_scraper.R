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

# get the link for each library
card_page <- read_html("https://librarytechnology.org/libraries/ulc/")
lib_links <- card_page %>% html_nodes("figcaption>a") %>% html_attr("href")

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
                         Homepage = library_link,
                         Catalog = catalog_link)
  # get the vendor info
  table <- html_node(webpage, xpath = "//table[.//th[contains(text(), 'Technology Profile')]]")
  rows <- html_nodes(table, "tr:nth-child(n+3)") # don't grab td
  header_values_raw <- html_text(html_nodes(rows, "th"))
  header_values <- header_values_raw %>% make.unique(sep = "_") %>% rep(each = 2)
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
