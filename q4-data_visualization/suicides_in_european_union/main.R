# install packages
# install.packages('readxl', dependencies = TRUE)
# install.packages('tidyr', dependencies = TRUE)
# install.packages('plyr', dependencies = TRUE)
# install.packages('ggplot2', dependencies = TRUE)
# install.packages('ggimage', dependencies = TRUE)
# install.packages('directlabels', dependencies = TRUE)
# install.packages('dplyr', dependencies = TRUE)
# install.packages('corrplot', dependencies = TRUE)
# install.packages('rgdal', dependencies = TRUE)

# libraries
library(readxl)
library(tidyr)
library(plyr)
library(ggplot2)
library(ggimage)
library(directlabels)
library(dplyr)
library(corrplot)
library(rgdal)

# -------------------------------------------------------------------------------
# Define functions to read the data
# -------------------------------------------------------------------------------

# function to read excel files
read_data_from_excel_format = function(path, sheet, columns, num_columns, skip = 0) {
  df = read_excel(path, sheet = sheet, col_types = 'text', skip = skip)
  df = df[-1,]
  df = pivot_longer(df, cols = starts_with('2'))
  colnames(df) = columns
  df[num_columns] = sapply(df[num_columns], function(x) as.numeric(as.character(x)))
  return(df)
}

# function to read csv files
read_data_from_csv_format = function(path, num_columns) {
  df = read.csv(path, header = TRUE)
  df[num_columns] = sapply(df[num_columns], function(x) as.numeric(as.character(x)))
  return(df)
}

# -------------------------------------------------------------------------------
# Read the data
# -------------------------------------------------------------------------------

# country metadata
df_country_metadata = read.csv('data/country_metadata.csv', header = TRUE)

# gdp per capita
df_gdp = read_data_from_excel_format(path = 'data/eurostat_gdp_pps.xlsx',
                                     sheet = 'Sheet 1',
                                     columns = c('country','year','gdp'),
                                     num_columns = c('year','gdp'),
                                     skip = 8)

# suicide rates
df_suicides = read_data_from_excel_format(path = 'data/eurostat_suicide_rate_by_sex.xlsx',
                                          sheet = 'Sheet 1',
                                          columns = c('country','year','suicide_rate'),
                                          num_columns = c('year','suicide_rate'),
                                          skip = 10)

# unemployment rates
df_unemployment = read_data_from_excel_format(path = 'data/eurostat_unemployment.xlsx',
                                              sheet = 'Sheet 1',
                                              columns = c('country','year','unemployment'),
                                              num_columns = c('year','unemployment'),
                                              skip = 9)

# -------------------------------------------------------------------------------
# Preprocess the data
# -------------------------------------------------------------------------------

# combine dataframes
to_combine = list(df_gdp, df_suicides, df_unemployment)
df_combined = join_all(to_combine, by = c('country','year'), type = 'left')

# combine metadata and dataframes
to_combine = list(df_country_metadata, df_combined)
df_combined = join_all(to_combine, by = 'country', type = 'left')

# keep common years
years_to_keep = c('2011','2012','2013','2014','2015','2016','2017')
df = df_combined[df_combined$year %in% years_to_keep,]

# percentage change YoY
df$suicide_rate_movement = with(df, ave(suicide_rate, iso_name, FUN = function(x) c(NA, diff(x)/x[-length(x)])))*100
df$suicide_rate_movement = round(df$suicide_rate_movement,1)

# -------------------------------------------------------------------------------
# Graph 1 - Slide 3
# Lineplot
# Suicide rate in European Union
# -------------------------------------------------------------------------------

ggplot(df[df$iso_name == 'EU',], aes(x = year, y = suicide_rate)) +
  geom_line(color = 'black', linewidth = 1) +
  geom_point(color = 'black', size = 3) +
  geom_text(aes(label = suicide_rate), vjust = -3, hjust = 0.5, color = 'black', size=5) +
  scale_x_continuous(breaks = seq(2011, 2017, by = 1)) +
  coord_cartesian(ylim = c(10, 13)) +
  labs(x = NULL,
       y = NULL,
       title = 'Suicide rate in European Union') +
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        axis.text.x = element_text(size = 12),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 2 - Slide 3
# Lineplot
# Annual percentage change in suicide rate in European Union
# -------------------------------------------------------------------------------

ggplot(data = df[df$iso_name == 'EU',], aes(x = year, y = suicide_rate_movement)) +
  geom_bar(stat = 'identity', fill = 'black') +
  geom_text(aes(label = suicide_rate_movement), color = '#E0E0E0', size = 4, vjust = ifelse(df[df$iso_name == 'EU',]$suicide_rate_movement >= 0,3,-1)) +
  geom_hline(yintercept = 0, color = 'black', size = 1) +
  scale_x_continuous(breaks = seq(2011, 2017, by = 1)) +
  labs(x = NULL,
       y = '% Change',
       title = 'Annual percentage change in suicide rate') +
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        axis.text.x = element_text(size = 12),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 3 - Slide 5
# Heatmap
# Suicide rate in European countries between 2011 - 2017
# -------------------------------------------------------------------------------

ggplot(data = df[!df$iso_name == 'EU',], aes(x = year, y = country_name, fill = ntile(suicide_rate,50))) +
  geom_raster() + 
  scale_fill_distiller(palette = 'Reds', direction = 1) +
  scale_x_continuous(breaks = seq(2011,2017, by = 1)) +
  guides(fill = guide_legend(nrow = 1,
                             title.position = 'top',
                             title.hjust = 0.5,
                             label.position = 'bottom')) +
  labs(x = NULL,
       y = NULL,
       fill = 'max value of each bin',
       title = 'Suicide rate in EU countries') + 
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        legend.title = element_text(size = 10),
        legend.position = 'top',
        legend.justification = 'center',
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = 'white'))

# -------------------------------------------------------------------------------
# Graph 4 - Slide 6
# Facet wrap
# Suicide rate trendline in European countries between 2011 - 2017
# -------------------------------------------------------------------------------

ggplot(data = df[!df$iso_name == 'EU',], aes(x = year, y = suicide_rate)) + 
  geom_line(color = 'red', size = 0.5) + 
  geom_point(color = 'red', size = 1) +
  geom_smooth(method = 'lm', color = 'darkgrey', size = 0.5, linetype = 'dashed', se = FALSE) +
  facet_wrap(~ country_name , scales = 'free_y') +
  labs(x = NULL,
       y = NULL,
       title = 'Suicide rate trendline by country',
       subtitle = 'From 2011 to 2017') +
  theme(plot.title = element_text(size = 14, hjust = 0.0, vjust = 1),
        axis.text.x = element_blank(),
        axis.text.y = element_blank(),
        axis.ticks.x = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        strip.background = element_rect(fill = 'grey'),
        strip.text = element_text(color = 'black'))

# -------------------------------------------------------------------------------
# Graph 5 - Slide 7
# Scatterplot
# Suicide rate trendline in European countries between 2011 - 2017
# -------------------------------------------------------------------------------

comparison_between_two_years = function(df, year1, year2) {
  
  eu_average1 = df$suicide_rate[df$iso_name == 'EU' & df$year == year1]
  eu_average2 = df$suicide_rate[df$iso_name == 'EU' & df$year == year2]
  
  df = df[!df$iso_name == 'EU',]
  arr1 = df[df$year == year1,]$suicide_rate
  arr2 = df[df$year == year2,]$suicide_rate
  names = df[df$year == year2,]$country_name
  df_compare = data.frame(arr1, arr2, names)
  df_compare$has_decreased = as.factor(ifelse(df_compare$arr2 > df_compare$arr1,0,1))
  
  ggplot(data = df_compare, aes(x = arr1, y = arr2)) +
    geom_point(aes(color = has_decreased)) + 
    geom_text(aes(x = arr1, y = arr2, label = names, color = has_decreased), vjust = -1, size = 3) +
    scale_color_manual(labels = c('Increased', 'Decreased'), values = c('red','darkgreen')) +
    geom_abline(slope = 1, intercept = 0, color = 'black', size = 0.5) +
    geom_vline(xintercept = eu_average1, linetype = 'dashed', color = 'black', size = 0.1) +
    geom_hline(yintercept = eu_average2, linetype = 'dashed', color = 'black', size = 0.1) +
    coord_cartesian(xlim = c(2,35),
                    ylim = c(2,35)) +
    labs(x = year1,
         y = year2,
         title = paste('Suicide rate comparison between', year1, 'and', year2)) + 
    theme(plot.title = element_text(size = 14, hjust = 0.5),
          legend.position = 'none',
          axis.text = element_text(size = 14),
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          panel.background = element_rect(fill = '#f1f1f1', color = 'black'))
}

comparison_between_two_years(df, 2011, 2017)

# -------------------------------------------------------------------------------
# Graph 6 - Slide 8
# Map
# Suicide rate density map in European countries in 2017
# -------------------------------------------------------------------------------

map = readOGR(dsn = 'data/TM_WORLD_BORDERS_SIMPL-0.3.shp',)
europe = map[map@data$REGION == 150,]
data = fortify(europe)
europe@data$id = rownames(europe@data)

suicide_rate_density_map = function(df, polygon, data, year) {
  
  df = df[df$year==year,]
  df = left_join(df, polygon@data, by = c('iso_name'='ISO3'), type = 'left')
  df = left_join(data, df, by = c('id'))
  labels = df[!duplicated(df[,c('country_name')]),]
  
  graph = ggplot() +
    geom_polygon(data = df, aes(long, lat, group = group, fill = ntile(suicide_rate,50)), color = 'black', size = 0.7) +
    geom_label(data = df, mapping = aes(x = long_center, y = lat_center, label = country_name), vjust = 0.5, hjust = 1.0, alpha = 0.5) +
    scale_fill_distiller(palette = 'Reds', direction = 1) +
    coord_cartesian(xlim = c(-10,50),
                    ylim = c(33,70)) +
    guides(fill = guide_legend(nrow = 1,
                               title.position = 'top',
                               title.hjust = 1,
                               label.position = 'bottom')) +
    labs(x = NULL,
         y = NULL) + 
    theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
          legend.position = 'none',
          axis.ticks.x = element_blank(),
          axis.ticks.y = element_blank(),
          axis.text.x = element_blank(),
          axis.text.y = element_blank(),
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          panel.background = element_rect(fill = 'white'),
          strip.background = element_rect(color = "#9E7777", fill = "#9E7777"),
          strip.text = element_text(color = 'white'))
  
  return(graph)
}

suicide_rate_density_map(df, europe, data, 2017)

# -------------------------------------------------------------------------------
# Graph 7 - Slide 9
# Barplot
# Suicide rate in European countries, compared to EU average, in 2017
# -------------------------------------------------------------------------------

suicide_rates_compared_to_eu_average = function(df, year) {
  
  df = df[df$year == year,]
  eu_average = df$suicide_rate[df$iso_name == 'EU']
  df = df[!df$iso_name == 'EU',]
  df = df[order(df$suicide_rate, decreasing = TRUE),]
  df$threshold = ifelse(df$suicide_rate > eu_average, 'More than EU average', 'Less than EU average')
  df$seq = seq(1, nrow(df))
  
  ggplot(df, aes(x = seq, y = suicide_rate, fill = threshold)) +
    geom_bar(stat = 'identity') +
    geom_text(aes(label = country_name), vjust = 0.4, hjust = 1.1, color = 'white', size = 3) +
    scale_fill_manual(values = c('#0000CC','#CC0000')) +
    scale_y_continuous(breaks = seq(0, 30, by = 5)) +
    coord_flip() +
    labs(x = NULL,
         y = NULL,
         title = 'Suicide Rate by Country (2017)',
         subtitle = 'Compared to EU average') +
    theme(plot.title = element_text(size = 14, hjust = 0.0, vjust = 1), 
          legend.position = c(.83,.93),
          legend.title = element_blank(),
          axis.text.y = element_blank(),
          axis.ticks.y = element_blank(),
          axis.line = element_line(colour = 'black'),
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          panel.background = element_rect(fill = 'white'))
}

suicide_rates_compared_to_eu_average(df, 2017)

# -------------------------------------------------------------------------------
# Graph 8 - Slide 11
# Lineplot
# Suicide rate in Greece
# -------------------------------------------------------------------------------

ggplot(df[df$iso_name == 'GRC',], aes(x = year, y = suicide_rate)) +
  geom_line(color = 'darkblue', linewidth = 1) +
  geom_point(color = 'darkblue', size = 3) +
  geom_text(aes(label = suicide_rate), vjust = -3, hjust = 0.5, color = 'darkblue', size=5) +
  scale_x_continuous(breaks = seq(2011, 2017, by = 1)) +
  coord_cartesian(ylim = c(3,6)) +
  labs(x = NULL,
       y = NULL,
       title = 'Suicide rate in Greece') +
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        axis.text.x = element_text(size = 14),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 9 - Slide 11
# Lineplot
# Annual percentage change in suicide rate in Greece
# -------------------------------------------------------------------------------

ggplot(data = df[df$iso_name == 'GRC',], aes(x = year, y = suicide_rate_movement)) +
  geom_bar(stat = 'identity', fill = 'darkblue') +
  geom_text(aes(label = suicide_rate_movement), color = '#E0E0E0', size = 4, vjust = ifelse(df[df$iso_name == 'GRC',]$suicide_rate_movement >= 0,3,-1)) +
  geom_hline(yintercept = 0, color = 'black', size = 1) +
  scale_x_continuous(breaks = seq(2011, 2017, by = 1)) +
  labs(x = NULL,
       y = '% Change',
       title = 'Annual percentage change in suicide rate') +
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        axis.text.x = element_text(size = 14),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 10 - Slide 12
# Lineplot
# Unemployment rate in Greece
# -------------------------------------------------------------------------------

ggplot(df[df$iso_name == 'GRC',], aes(x = year, y = unemployment)) +
  geom_line(stat = 'identity', color = 'darkblue', linewidth = 1) +
  geom_point(color = 'darkblue', size = 3) +
  geom_text(aes(label = unemployment), vjust = -2, hjust = 0.5, color = 'darkblue', size = 5) +
  scale_x_continuous(breaks = seq(2011, 2017, by = 1)) +
  coord_cartesian(ylim = c(15,30)) +
  labs(x = NULL,
       y = NULL,
       title = 'Unemployment Rate in Greece') +
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        axis.text.x = element_text(size = 14),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 11 - Slide 13
# Lineplot
# GDP per capita in Greece
# -------------------------------------------------------------------------------

ggplot(df[df$iso_name == 'GRC',], aes(x = year, y = gdp)) +
  geom_line(stat = 'identity', color = 'darkblue', linewidth = 1) +
  geom_point(color = 'darkblue', size = 3) +
  geom_text(aes(label = gdp), vjust = -2, hjust = 0.5, color = 'darkblue', size = 5) +
  scale_x_continuous(breaks = seq(2011, 2017, by = 1)) +
  coord_cartesian(ylim = c(62,80)) +
  labs(x = NULL,
       y = NULL,
       title = 'GDP per Capita in Greece') +
  theme(plot.title = element_text(size = 14, hjust = 0.5, vjust = 1),
        axis.text.x = element_text(size = 14),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 12 - Slide 14
# Lineplot
# Correlation between suicide rate and unemployment rate in Greece
# -------------------------------------------------------------------------------

df_ur = df[df$iso_name == 'GRC',]
df_ur = df_ur[c('year','unemployment','suicide_rate')]
colnames(df_ur) = c('year','x','y')
linear.model = lm(y ~ x, df_ur)
exp.model = lm(y ~ exp(x), df_ur)
linear.model.df = data.frame(x = df_ur$x, y = fitted(linear.model))

ggplot(data = df_ur, aes(x = x, y = y)) +
  geom_point() +
  geom_text(aes(x = x, y = y, label = year, vjust = -1, hjust = 0.5), size=3) +
  geom_line(data = linear.model.df, aes(x, y, color = 'Linear Model'), size = 1, linetype = 2, color = 'darkgrey') +
  geom_smooth(method = 'lm', aes(color = 'Exp Model'), formula = (y ~ exp(x)), se = FALSE, linetype = 1, color = 'darkblue') +
  labs(x = 'Unemployment Rate',
       y = 'Suicide Rate',
       title = 'Suicide Rate vs Unemployment Rate') +
  theme(plot.title = element_text(size = 14, hjust = 0.5), 
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

# -------------------------------------------------------------------------------
# Graph 13 - Slide 14
# Lineplot
# Correlation between suicide rate and GDP per capita in Greece
# -------------------------------------------------------------------------------

df_gdp = df[df$iso_name == 'GRC',]
df_gdp = df_gdp[c('year','gdp','suicide_rate')]
colnames(df_gdp) = c('year','x','y')
linear.model = lm(y ~ x, df_gdp)
exp.model = lm(y ~ exp(x), df_gdp)
linear.model.df = data.frame(x = df_gdp$x, y = fitted(linear.model))

ggplot(data = df_gdp, aes(x = x, y = y)) +
  geom_point() +
  geom_text(aes(x = x, y = y, label = year, vjust = -1, hjust = 0.5), size=3) +
  geom_line(data = linear.model.df, aes(x, y, color = 'Linear Model'), size = 1, linetype = 2, color = 'darkgrey') +
  geom_smooth(method = 'lm', aes(color = 'Exp Model'), formula = (y ~ exp(x)), se = FALSE, linetype = 1, color = 'darkblue') +
  labs(x = 'GDP',
       y = 'Suicide Rate',
       title = 'Suicide Rate vs GDP') +
  theme(plot.title = element_text(size = 14, hjust = 0.5), 
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.background = element_rect(fill = '#E0E0E0', color = 'black'))

###################################### END ######################################