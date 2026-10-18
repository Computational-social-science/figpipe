#.rs.restartR()
rm(list=ls())
gc(reset=T)
rm(list=ls())

# Packages ------------
library("dplyr")
library("ggplot2")
library("asnipe")
library("igraph")
library("foreach")
library("doParallel")

# Source - https://www.r-bloggers.com/2013/02/arc-diagrams-in-r-les-miserables/
# Source - https://rdrr.io/github/gastonstat/arcdiagram/f/vignettes/introduction.Rmd
#devtools::install_github('gastonstat/arcdiagram')
library('arcdiagram')
library(igraph)

# Read-in Data --------
## Data | List of Countries ---------

Core_Country <- c("US", #US
                  "GB", #UK
                  "CN", #China
                  "DE", #Germany
                  "JP", #Japan
                  "AU", #Australia
                  "AT", #Austria
                  "BE", #Belgium
                  "CA", #Canada
                  "DK", #Denmark
                  "FI", #Finland
                  "FR", #France
                  "IS", #Iceland
                  "IE", #Ireland
                  "IT", #Italy
                  "IL", #Israel
                  "NL", #Netherlands
                  "NZ", #New Zealand
                  "NO", #Norway
                  "PT", #Portugal
                  "SG", #Singapore
                  "KR", #South Korea
                  "ES", #Spain
                  "SE", #Sweden
                  "CH", #Switzerland 
                  "TW" #Taiwan
)

## Data | ISO2 with full names -------

# N.B., DO NOT load the package 'raster' it creates a lot of conflicts with dplyr

iso2_name_df <- raster::ccodes()%>%
  dplyr::select(NAME,ISO2)%>%
  tidyr::drop_na()

## Data | Read in Raw Discursive Influence Data -------

Discursive_Influence_Raw_df <- read.csv("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/OUTPUT_Python_MultiPaper_Discursive_Influence_2024_03_19.csv")

## Data | Censored and Sample Terms --------

Sample_of_Censored_Terms_df <- Discursive_Influence_Raw_df %>%
  dplyr::group_by(Term,Year) %>%
  dplyr::mutate(Single_or_Multiple_Countries = length(unique(Influencer))) %>% 
  ungroup()%>%
  subset(Single_or_Multiple_Countries>=1) %>%
  subset(Number_of_Papers_with_Term_and_Cite>=10)%>%
  select(Term,Number_of_Papers_with_Term_and_Cite)%>%
  arrange(-Number_of_Papers_with_Term_and_Cite)%>%
  unique()


Sample_Terms <- c(head(Sample_of_Censored_Terms_df,3) %>% .$Term,
                  Sample_of_Censored_Terms_df %>% subset(Number_of_Papers_with_Term_and_Cite<200) %>% 
                    head(3) %>% .$Term,
                  Sample_of_Censored_Terms_df %>% subset(Number_of_Papers_with_Term_and_Cite<50) %>% head(10) %>% .$Term)


Censored_Terms_df <-Sample_of_Censored_Terms_df %>%
  select(Term)

## Output | Censored Term List -----------


# write.csv(Sample_of_Censored_Terms_df,"/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/OUTPUT_R_Censored_Terms_for_Table_Data_2024_03_19.csv",row.names = F)

## Data | Read in Raw Attributional Influence -------
Attributional_Influence_Raw_df <- read.csv("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/OUTPUT_Python_MultiPaper_Attributional_Influence_2024_03_19.csv") 


## Data | Censor Attributional and Discursive Influence Edgelists ------
Discursive_Influence_df <- Discursive_Influence_Raw_df%>%
  merge(.,Censored_Terms_df,by=c("Term")) %>%
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Discursive_Influence = sum(Weight))%>%
  arrange(Year)%>%
  as.data.frame()

Attributional_Influence_df <- Attributional_Influence_Raw_df%>%
  merge(.,Censored_Terms_df,by=c("Term"))%>%
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Attributional_Influence = sum(Influenced_Weights))%>%
  arrange(Year) %>%
  as.data.frame()


# Influenced_All_Countries_List <- rbind((Discursive_Influence_df %>% select(Influenced) %>% unique()),
#                                        (Attributional_Influence_df %>% select(Influenced) %>% unique())) %>%
#   unique() %>%
#   subset(is.na(.)==F)
# 
# Influencer_All_Countries_List <- rbind((Discursive_Influence_df %>% select(Influencer) %>% unique()),
#                                        (Attributional_Influence_df %>% select(Influencer) %>% unique())) %>%
#   unique() %>%
#   subset(is.na(.)==F)
# 
# All_Countries_df <- merge(Influencer_All_Countries_List,
#       data.frame("Year"=1990:2013))%>%
#   merge(.,Influenced_All_Countries_List) %>%
#   subset(Influencer!=Influenced)%>%
#   subset(Influencer!='')%>%
#   subset(Influenced!='')


Influence_df <- merge(Discursive_Influence_df,Attributional_Influence_df,
                      by=c("Influencer","Influenced","Year"),
                      all.x=T,
                      all.y=T)%>%
  #merge(All_Countries_df,.,
  #by=c("Influencer","Influenced","Year"),all.x=T) %>%
  replace(is.na(.), 0) %>%
  subset(Influencer!=Influenced) %>%
  arrange(Year) %>%
  dplyr::group_by(Year) %>%
  dplyr::mutate(DI_Scale = scale(Discursive_Influence),
                AI_Scale = scale(Attributional_Influence)) %>%
  ungroup()%>%
  dplyr::mutate(Relative_Influence = DI_Scale-AI_Scale)%>%
  mutate(Influencer_CP = case_when(Influencer%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  mutate(Influenced_CP = case_when(Influenced%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  as.data.frame()

## Data | ISO Region ---------

ISO_Region_df <-   raster::ccodes() %>%
  select(ISO2,UNREGION1) %>%
  dplyr::mutate(UNREGION1 = case_when(ISO2%in%c("US") ~ "United\nStates",
                                      ISO2%in%c("DE","AT","BE","DK","FI","FR","IS","IE","IT","NL","NO","PT","ES","SE","CH","GR","IL") ~ "Core\nEurope",
                                      ISO2 %in% c("AU","NZ","CA","GB") ~ "Core\nCW",
                                      
                                      ISO2%in%c("CN") ~ "China",
                                      ISO2%in%c("JP","SG","KR","TW","CN") ~ "Core\nAsia",
                                      UNREGION1%in%c("Eastern Asia","South-Eastern Asia","Western Asia","Southern Asia","Central Asia") ~ "Periphery\nAsia",
                                      UNREGION1%in%c("Eastern Europe","Northern Europe","Southern Europe","Western Europe") ~ "Periphery\nEurope",
                                      UNREGION1%in%c("Caribbean","South America","Central America","Northern America") ~ "Latin\nAmerica",
                                      UNREGION1%in%c("Southern Africa","Western Africa","Middle Africa","Eastern Africa","Northern Africa") ~ "Africa",
                                      UNREGION1%in%c("Polynesia","Micronesia","Melanesia") ~ "Oceania",
                                      TRUE ~ UNREGION1))%>%
  as.data.frame()

## Supplementary Information | Data | Domestic Authors Only ---------------

SI_Domestic_Sample_of_Censored_Terms_df <- Discursive_Influence_Raw_df %>%
  dplyr::group_by(Term,Year) %>%
  dplyr::mutate(Single_or_Multiple_Countries = length(unique(Influencer))) %>% 
  ungroup()%>%
  
  # Influencer should only be domestic, so only "single" country
  subset(Single_or_Multiple_Countries==1) %>%
  
  subset(Number_of_Papers_with_Term_and_Cite>=10)%>%
  select(Term,Number_of_Papers_with_Term_and_Cite)%>%
  arrange(-Number_of_Papers_with_Term_and_Cite)%>%
  unique()

SI_Domestic_Censored_Terms_df <- SI_Domestic_Sample_of_Censored_Terms_df %>%
  select(Term)

SI_Domestic_Discursive_Influence_df <- Discursive_Influence_Raw_df%>%
  merge(.,SI_Domestic_Censored_Terms_df,by=c("Term")) %>%
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Discursive_Influence = sum(Weight))%>%
  arrange(Year)%>%
  as.data.frame()

SI_Domestic_Attributional_Influence_df <- Attributional_Influence_Raw_df%>%
  
  # Influencer should only be domestic, so only "single" country
  dplyr::group_by(Term,Year) %>%
  dplyr::mutate(Single_or_Multiple_Countries = length(unique(Influencer))) %>% 
  ungroup()%>%
  subset(Single_or_Multiple_Countries==1) %>%

  merge(.,SI_Domestic_Censored_Terms_df,by=c("Term"))%>%
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Attributional_Influence = sum(Influenced_Weights))%>%
  arrange(Year) %>%
  as.data.frame()

SI_Domestic_Influence_df <- merge(SI_Domestic_Discursive_Influence_df,
                                  SI_Domestic_Attributional_Influence_df,
                         by=c("Influencer","Influenced","Year"),
                         all.x=T,
                         all.y=T)%>%
  #merge(All_Countries_df,.,
  #by=c("Influencer","Influenced","Year"),all.x=T) %>%
  replace(is.na(.), 0) %>%
  subset(Influencer!=Influenced) %>%
  arrange(Year) %>%
  dplyr::group_by(Year) %>%
  dplyr::mutate(DI_Scale = scale(Discursive_Influence),
                AI_Scale = scale(Attributional_Influence)) %>%
  ungroup()%>%
  dplyr::mutate(Relative_Influence = DI_Scale-AI_Scale)%>%
  mutate(Influencer_CP = case_when(Influencer%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  mutate(Influenced_CP = case_when(Influenced%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  as.data.frame()

## Supplementary Information | Data | Uncited or Cited ----------------

SI_Sample_of_Censored_Terms_df <- Discursive_Influence_Raw_df %>%
  dplyr::group_by(Term,Year) %>%
  dplyr::mutate(Single_or_Multiple_Countries = length(unique(Influencer))) %>% 
  ungroup()%>%
  subset(Single_or_Multiple_Countries>=1) %>%
  subset(Number_of_Papers_with_Term_and_Cite>=0)%>%
  select(Term,Number_of_Papers_with_Term_and_Cite)%>%
  arrange(-Number_of_Papers_with_Term_and_Cite)%>%
  unique()

SI_Censored_Terms_df <-SI_Sample_of_Censored_Terms_df %>%
  select(Term)

Discursive_SI_Influence_df <- Discursive_Influence_Raw_df%>%
  merge(.,SI_Censored_Terms_df,by=c("Term")) %>%
  
  # Only First Apperance
  dplyr::group_by(Term) %>%
  dplyr::slice_min(Year,with_ties = T) %>%
  
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Discursive_Influence = sum(Weight))%>%
  arrange(Year)%>%
  as.data.frame()


Attributional_SI_Influence_df <- Attributional_Influence_Raw_df%>%
  merge(.,SI_Censored_Terms_df,by=c("Term"))%>%
  # Only First Apperance
  dplyr::group_by(Term) %>%
  dplyr::slice_min(Year,with_ties = T) %>%
  
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Attributional_Influence = sum(Influenced_Weights))%>%
  arrange(Year) %>%
  as.data.frame()
  
Influence_SI_df <- merge(Discursive_SI_Influence_df,Attributional_SI_Influence_df,
                      by=c("Influencer","Influenced","Year"),
                      all.x=T,
                      all.y=T)%>%
  #merge(All_Countries_df,.,
  #by=c("Influencer","Influenced","Year"),all.x=T) %>%
  replace(is.na(.), 0) %>%
  subset(Influencer!=Influenced) %>%
  arrange(Year) %>%
  dplyr::group_by(Year) %>%
  dplyr::mutate(DI_Scale = scale(Discursive_Influence),
                AI_Scale = scale(Attributional_Influence)) %>%
  ungroup()%>%
  dplyr::mutate(Relative_Influence = DI_Scale-AI_Scale)%>%
  mutate(Influencer_CP = case_when(Influencer%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  mutate(Influenced_CP = case_when(Influenced%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  as.data.frame()

## Supplementary Information | Data | Normalized by Term -----

Discursive_SI_TermNormed_Influence_df <- Discursive_Influence_Raw_df%>%
  merge(.,Censored_Terms_df,by=c("Term")) %>%
  
  # Term Normalized
  dplyr::group_by(Term) %>%
  mutate(Weight_Percent = Weight/sum(Weight))%>%
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Discursive_Influence = sum(Weight_Percent))%>%
  arrange(Year)%>%
  as.data.frame()


Attributional_SI_TermNormed_Influence_df <- Attributional_Influence_Raw_df%>%
  merge(.,Censored_Terms_df,by=c("Term"))%>%
  
  # Term Normalized
  dplyr::group_by(Term) %>%
  mutate(Weight_Percent = Influenced_Weights/sum(Influenced_Weights))%>%
  
  dplyr::group_by(Influencer,Influenced,Year)%>%
  dplyr::summarise(Attributional_Influence = sum(Weight_Percent))%>%
  arrange(Year) %>%
  as.data.frame()


Influence_SI_TermNormed_df <- merge(Discursive_SI_TermNormed_Influence_df,Attributional_SI_TermNormed_Influence_df,
                         by=c("Influencer","Influenced","Year"),
                         all.x=T,
                         all.y=T)%>%
  #merge(All_Countries_df,.,
  #by=c("Influencer","Influenced","Year"),all.x=T) %>%
  replace(is.na(.), 0) %>%
  subset(Influencer!=Influenced) %>%
  arrange(Year) %>%
  dplyr::group_by(Year) %>%
  dplyr::mutate(DI_Scale = scale(Discursive_Influence),
                AI_Scale = scale(Attributional_Influence)) %>%
  ungroup()%>%
  dplyr::mutate(Relative_Influence = DI_Scale-AI_Scale)%>%
  mutate(Influencer_CP = case_when(Influencer%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  mutate(Influenced_CP = case_when(Influenced%in%Core_Country~"Core",
                                   TRUE ~ "Periphery"))%>%
  as.data.frame()

# Statistics -------------
## Data  ----------

Influence_Statistics_Raw_df <- read.csv("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/OUTPUT_Python_MultiPaper_Number_of_Cites_per_Influencer_Paper_Attributional_Influence_2024_03_19.csv")


Attributional_Influence_Statistics_df <- Influence_Statistics_Raw_df %>%
  merge(Censored_Terms_df,.,by=c("Term"))%>%
  select(Term,Number_of_Citations_per_Influencer_Paper)%>%
  dplyr::group_by(Term)%>%
  dplyr::summarize(Number_of_Cites = sum(Number_of_Citations_per_Influencer_Paper)) %>%
  as.data.frame()

Discursive_Influence_Statistics_df <- Influence_Statistics_Raw_df %>%
  merge(Censored_Terms_df,.,by=c("Term"))%>%
  select(Term,Influencer_Paper_ID)%>%
  dplyr::group_by(Term)%>%
  dplyr::summarize(Number_of_Papers = length(Influencer_Paper_ID)) %>%
  as.data.frame()

## Output | Censored Terms -------

#write.csv(Censored_Terms_df,"/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/OUTPUT_List_of_Censored_Terms_2024_03_19.csv",row.names = F)

## Plot | Papers by Country ------

## Number | Number of Papers with Discursive Influence ------
Censored_Terms_df %>%
  merge(.,Influence_Statistics_Raw_df %>%
          select(Term,Influencer_Paper_ID)%>%
          unique(),by=c("Term")) %>%
  select(Influencer_Paper_ID) %>%
  unique()%>%
  count()
# 567,258

 
Percentage_Terms_Country_df <- Censored_Terms_df %>%
  merge(.,Discursive_Influence_Raw_df %>%
  select(Term,Year,Influencer)%>%
  unique(),by=c("Term")) %>%
  select(Influencer)%>%
  dplyr::group_by(Influencer)%>%
  summarize(Count = n())%>%
  mutate(Percent = Count/sum(Count)) %>%
  dplyr::arrange(-Percent)


PLOT_Percent_Papers_by_Country <- Percentage_Terms_Country_df %>%
  dplyr::top_n(20,Percent) %>%
  merge(.,iso2_name_df%>%
          rename(Influencer=ISO2),
        by=c("Influencer")) %>%
  ggplot(data=.,aes(x=reorder(NAME,-Percent),y=Percent)) + 
  geom_bar(stat="identity") +
  geom_text(aes(label=paste0(round(100*Percent,0),"%")), 
            position=position_dodge(width=0.9), vjust=-0.25)+
  theme_bw()+
  scale_y_continuous(labels = scales::percent,expand = expansion(mult = c(0, 0.05)))+
  theme(panel.border = element_blank(), 
       panel.grid.major = element_blank(),
       panel.grid.minor = element_blank(), 
       axis.line = element_blank()) +
  theme(legend.position="top")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black"))+
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1, size=12))+
  xlab("")+
  ylab("Percent of Term Papers")

## Plot | Attributional Influence Histogram ----------

# Attributional_Influence_Statistics_df%>%
#   ggplot(., aes(x=Number_of_Cites)) + 
#   scale_x_log10(expand=c(0,0),
#                 breaks = scales::trans_breaks("log10", function(x) 10^x),
#                 labels = scales::trans_format("log10", 
#                                               scales::math_format(10^.x)))+   scale_y_continuous(expand=c(0,0))+
#   geom_histogram()+
#   geom_vline(xintercept=round(mean(Attributional_Influence_Statistics_df$Number_of_Cites),2),
#              linetype="dashed")+
#   ggsci::scale_color_aaas()+
#   theme_bw()+
#   theme(panel.border = element_blank(), 
#         axis.line = element_line(colour = "black")) +
#   theme(legend.position="bottom")+
#   theme(strip.background = element_blank(), strip.placement = "outside")+
#   theme(legend.background = element_rect(colour = "black")) +
#   theme(legend.title=element_blank())+
#   guides(colour = guide_legend(override.aes = list(alpha = 1)))+
#   ylab("Frequency")+
#   xlab("Number of Papers Citing Works with a Specific Term in Its Title or Abstract")


## Plot | Discursive Influence Histogram ----------

# Discursive_Influence_Statistics_df%>%
# ggplot(., aes(x=Number_of_Papers)) + 
#   scale_x_log10(expand=c(0,0),
#                 breaks = scales::trans_breaks("log10", function(x) 10^x),
#                 labels = scales::trans_format("log10", 
#                                               scales::math_format(10^.x)))+   scale_y_continuous(expand=c(0,0))+
#   geom_histogram()+
#   geom_vline(xintercept=round(mean(Discursive_Influence_Statistics_df$Number_of_Papers),2),
#              linetype="dashed")+
#   ggsci::scale_color_aaas()+
#   theme_bw()+
#   theme(panel.border = element_blank(), 
#         axis.line = element_line(colour = "black")) +
#   theme(legend.position="bottom")+
#   theme(strip.background = element_blank(), strip.placement = "outside")+
#   theme(legend.background = element_rect(colour = "black")) +
#   theme(legend.title=element_blank())+
#   guides(colour = guide_legend(override.aes = list(alpha = 1)))+
#   ylab("Frequency")+
#   xlab("Number of Papers with a Specified Term in Its Abstract or the Title")


## Numbers | Number of Terms ------

merge(Attributional_Influence_Statistics_df,Discursive_Influence_Statistics_df,by=c("Term")) %>% dim()
# 10,046

## Numbers | Average Numbers of Term and Attributional Papers ------

merge(Attributional_Influence_Statistics_df,Discursive_Influence_Statistics_df,by=c("Term")) %>%
  summarize(Attributional_Papers_per_Term_Mean = mean(Number_of_Cites,na.rm=T),
         Term_Papers_per_Term_Mean = mean(Number_of_Papers,na.rm=T))
# 1922 67

## Plot | Discursive v Attributional Influence -------


p1 <- merge(Attributional_Influence_Statistics_df,
      Discursive_Influence_Statistics_df,by=c("Term")) %>%
  
  ggplot(data=.,
         aes(x=Number_of_Papers,
             y=Number_of_Cites))+
  geom_hex()+
  geom_point(alpha=0)+
  scale_x_log10(expand=c(0,0),
                breaks = scales::trans_breaks("log10", function(x) 10^x),
                labels = scales::trans_format("log10", 
                                              scales::math_format(10^.x)))+ 
  scale_y_log10(expand=c(0,0),
                breaks = scales::trans_breaks("log10", function(x) 10^x),
                labels = scales::trans_format("log10", 
                                              scales::math_format(10^.x)))+
  # ggrepel::geom_label_repel(data=.%>%
  #                              subset(Term%in%Sample_Terms),
  #                            aes(label=Term),
  #                            fontface = 'bold', 
  #                            color ='red',
  #                            segment.color = "black",
  #                            direction="y",
  #                            nudge_x=0.25,
  #                            show.legend=F)+
  theme_bw()+
  ylab("Number of Attributional Papers per Term")+
xlab("Number of Term Papers per Term")+

  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position="bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  viridis::scale_fill_viridis()+
  ggpubr::stat_cor(method = "pearson",
                     p.accuracy = 0.001, 
                     r.accuracy = 0.01)

PLOT_Descriptive_Stats <- ggExtra::ggMarginal(p1,type="histogram", size=10)


## Plot | Attributional Influence by Country ------

# Discursive_Influence_Raw_df %>%
#   select(Term,Year,Influencer) %>%
#   unique() %>%
#   dplyr::mutate(Core_Periphery = case_when(Influencer %in% Core_Country ~ "Core",
#                                            TRUE ~ "Periphery"))%>%
#   dplyr::mutate(Time_Period = case_when(Year<=2005 ~ "1990-2005",
#                                         TRUE ~ "2006-2020"))%>%
#   dplyr::group_by(Core_Periphery,Influencer,Time_Period)%>%
#   dplyr::summarize(Number_of_Papers = length(Influencer))%>%
#   as.data.frame() %>%
#   ggplot(data=.,aes(x=Core_Periphery,y=Number_of_Papers))+
#   geom_boxplot()+
#   theme_bw()

## Plot | Discursive Influence by Country -------

# Centrality ------------
## Data | Centrality Dataframe -----------

Centrality_df <- Influence_df%>%
  dplyr::group_by(Influencer_CP,Influencer,Year)%>%
  dplyr::summarise(Centrality_DI = sum(Discursive_Influence),
                   Centrality_AI = sum(Attributional_Influence),
                   Centrality_RI = sum(Relative_Influence)
                   )%>%
  as.data.frame()

## Number | Number of Countries ---------------

Centrality_df %>% select(Influencer) %>% unique() %>% count()

## Data | Centrality by Core-Periphery Dataframe -----------

Centrality_CP_df <- Centrality_df %>%
  dplyr::group_by(Year)%>%
  dplyr::mutate(Centrality_AI = scale(Centrality_AI),
         Centrality_DI = scale(Centrality_DI)) %>%
  dplyr::group_by(Influencer_CP,Year)%>%
  dplyr::summarise(Centrality_RI_Mean = mean(Centrality_RI,na.rm=T),
                   Centrality_RI_SE = sd(Centrality_RI)/sqrt(length(Centrality_RI)),
                   Centrality_DI_Mean = mean(Centrality_DI,na.rm=T),
                   Centrality_DI_SE = sd(Centrality_DI)/sqrt(length(Centrality_DI)),
                   Centrality_AI_Mean = mean(Centrality_AI,na.rm=T),
                   Centrality_AI_SE = sd(Centrality_AI)/sqrt(length(Centrality_AI)))%>%
  as.data.frame()

## Plot | Discursive and Attributional Influence Centrality over Time by Core-Periphery -------------

PLOT_Influence_Centrality <- ggplot(data=Centrality_CP_df%>%
         select(Influencer_CP,Year,Centrality_DI_Mean,Centrality_DI_SE)%>%
         dplyr::rename(Mean = Centrality_DI_Mean,
                SE = Centrality_DI_SE) %>%
         mutate(Type = "Discursive Influence") %>%
         rbind(.,Centrality_CP_df%>%
                 select(Influencer_CP,
                        Year,
                        Centrality_AI_Mean,
                        Centrality_AI_SE)%>%
                 dplyr::rename(Mean = Centrality_AI_Mean,
                        SE = Centrality_AI_SE) %>%
                 mutate(Type = "Attributional Influence")),
       aes(x=Year,y=Mean,group=Influencer_CP,colour=Influencer_CP))+
  geom_point(size=4)+
  geom_ribbon(aes(ymin=Mean-SE,
                  ymax=Mean+SE),
              alpha=0.25,
              show.legend = F)+
  geom_smooth(show.legend = F, method="lm")+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left")+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Country Centrality\n(Z-Scores)")+
  xlab("Year")+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  #scale_y_log10(breaks = scales::trans_breaks("log10", function(x) 10^x),
  #              labels = scales::trans_format("log10", scales::math_format(10^.x)))+  
  ggsci::scale_color_aaas()+
  facet_wrap(~Type,scales="free_y")


## Plot | Relative Influence Centrality over Time by Core-Periphery -------------

PLOT_Relative_Influence_CorePeriphey <- ggplot(data=Centrality_CP_df,
       aes(x=Year,y=Centrality_RI_Mean,group=Influencer_CP,colour=Influencer_CP))+
  geom_point(size=4)+
    geom_ribbon(aes(ymin=Centrality_RI_Mean-Centrality_RI_SE,
                    ymax=Centrality_RI_Mean+Centrality_RI_SE),
                alpha=0.25,
                show.legend = F)+
  stat_smooth(method = 'lm', formula = y ~ poly(x,2), 
              show.legend = F)+
  geom_hline(yintercept = 0,linetype="dashed")+
    annotate("text", x = 2000, y = 3, label = "Greater\nDiscursive\nInfluence",size=6)+
    annotate("text", x = 2000, y = -1.2, label = "Greater\nAttributional\nInfluence",size=6)+
    #ylim(c(-1.25,4))+
    ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left")+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = c(0.2, 0.75))+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 6)))+
  ylab("Relative Influence\n(Z-Scores)")+
  xlab("Year")+
  ylim(c(-2,5))+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_aaas()

# Gini ------
## Plot | Attributional Influence  --------

PLOT_Gini_Attributional_Influence <- Centrality_df %>%
  dplyr::group_by(Year)%>%
  
  dplyr::summarise(Gini = ineq::Gini((Centrality_AI)-min(Centrality_AI)))%>%
  as.data.frame() %>%
  ggplot(data=.,aes(x=Year,y=Gini))+
  geom_point(size=4)+
  #geom_smooth(method="lm",show.legend = F)+
  stat_smooth(method='lm',formula = y ~ poly(x,3), 
              show.legend = F)+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left")+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Gini Coefficient\nCountry Centrality in Attributional Influence Networks")+
  xlab("Year")+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_aaas()


## Plot | Discursive Influence  --------

PLOT_Gini_Discursive_Influence <- Centrality_df %>%
  dplyr::group_by(Year)%>%
  dplyr::summarise(Gini = ineq::Gini((Centrality_DI)-min(Centrality_DI)))%>%
  as.data.frame() %>%
  ggplot(data=.,aes(x=Year,y=Gini))+
  geom_point(size=4)+
  #geom_smooth(method="lm",show.legend = F)+
  stat_smooth(method='lm',formula = y ~ poly(x,3), 
              show.legend = F)+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left")+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Gini Coefficient\nCountry Centrality in Discursive Influence Networks")+
  xlab("Year")+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_aaas()


## Plot | Relative Influence  --------

PLOT_Gini_Relative_Influence <- Centrality_df %>%
  dplyr::group_by(Year)%>%
  dplyr::summarise(Gini = ineq::Gini((Centrality_RI)-min(Centrality_RI)))%>%
  as.data.frame() %>%
  ggplot(data=.,aes(x=Year,y=Gini))+
  geom_point(size=4)+
  geom_smooth(method="lm",show.legend = F)+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left")+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Gini Coefficient\nCountry Centrality in Relative Influence Networks")+
  xlab("Year")+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_aaas()

# MRQAP ------- 
## Data | MRQAP --------

# https://stackoverflow.com/questions/38318139/run-a-for-loop-in-parallel-in-r
# https://stackoverflow.com/questions/41117127/r-parallel-programming-error-in-task-1-failed-could-not-find-function
# https://stackoverflow.com/questions/30248583/error-could-not-find-function
  
cores <- detectCores()
cl <- makeCluster(8, type = "FORK") #not to overload your computer
clusterCall(cl, function() library(magrittr))
registerDoParallel(cl)
  
MRQAP_Results_df <- data.frame()
  
# %dopar%
MRQAP_Results_df <- foreach(i = 1990:2013, .combine=rbind,.packages=c("dplyr","tidyr","asnipe","igraph"), .errorhandling = 'pass') %dopar% {
    
   year_ <- i
    
  Discursive_Influence_Matrix_Year <- Influence_df %>%
    subset(Year==year_)%>%
    select(Influencer,Influenced,Discursive_Influence) %>%
    dplyr::rename(weight=Discursive_Influence)%>%
    mutate(weight=scale(weight))%>%
    igraph::graph.data.frame(.,directed=TRUE)%>%
    igraph::as_adjacency_matrix(.,sparse=TRUE,attr = "weight")%>%
    as.matrix(.)
  
  Attributional_Influence_Matrix_Year <- Influence_df %>%
    subset(Year==year_)%>%
    select(Influencer,Influenced,Attributional_Influence) %>%
    dplyr::rename(weight=Attributional_Influence)%>%
    mutate(weight=scale(weight))%>%
    igraph::graph.data.frame(.,directed=TRUE)%>%
    igraph::as_adjacency_matrix(.,sparse=TRUE,attr = "weight")%>%
    as.matrix(.)

      model_ <- asnipe::mrqap.dsp(Discursive_Influence_Matrix_Year~Attributional_Influence_Matrix_Year, 
                                intercept = TRUE, 
                                directed = "directed",
                                diagonal = FALSE, 
                                test.statistic = "t-value",
                                tol = 1e-07, randomisations = 1000)
    
    coefficients_df <- data.frame(Beta=model_$coefficients,
                                  T_Statistics=model_$test.statistic,
                                  P_Values = model_$P.values,
                                  P_Greater = model_$P.greater,
                                  P_Lesser = model_$P.lesser,
                                  N=model_$n,
                                  AIC=model_$AIC)
    
    coefficients_df$Coefficients <- row.names(coefficients_df)
    row.names(coefficients_df) <- NULL
    
    coefficients_df$Year <- year_
    coefficients_df <- coefficients_df %>%
      mutate(Standard_Error = Beta/T_Statistics)    
    rbind(MRQAP_Results_df,coefficients_df)
    
  }
  
  stopCluster(cl)
  rm(cl)

## Number | Beta QAP -----
  
MRQAP_Results_df%>%
           filter(Coefficients=='Attributional_Influence_Matrix_Year') %>%
    select(Beta) %>% summarize(Beta_Mean = mean(Beta))
  
## Plot | MRQAP -------
  
PLOT_QAP <- ggplot(data=MRQAP_Results_df%>%
           filter(Coefficients=='Attributional_Influence_Matrix_Year'),
         aes(x=Year,y=Beta))+
    theme_bw()+
    geom_point(size=4)+
    ylim(c(0.9,1.01))+
    geom_hline(yintercept = 1,linetype="dashed",colour="red")+
    scale_x_continuous(breaks= scales::pretty_breaks())+
    ylab("QAP Beta Coefficients")+
    xlab("Year")+
    geom_ribbon(aes(ymin=Beta-Standard_Error,
                    ymax=Beta+Standard_Error),
                alpha=0.25,
                show.legend = F)+
    #geom_smooth(method='exp',formula=y~log1p(x))+
    stat_smooth(method='lm',formula = y ~ poly(x,4), 
                show.legend = F)+
    ggpubr::stat_cor(aes(group=1),
                     p.accuracy = 0.001,
                     r.accuracy = 0.01,
                     method = "pearson")+
    theme(panel.border = element_blank(), 
          axis.line = element_line(colour = "black")) +
    theme(legend.position="bottom")+
    theme(strip.background = element_blank(), strip.placement = "outside")+
    theme(legend.background = element_rect(colour = "black")) +
    theme(legend.title=element_blank())+
    guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))
  
# Dyad ----------
## Plot | Dyad by Core-Periphery --------
  
PLOT_Core_Periphery_Dyads <- Influence_df %>%

    dplyr::mutate(Dyad = case_when(Influencer_CP=="Core" & Influenced_CP=="Core" ~ "Core \u2192 Core",
                                   Influencer_CP=="Core" & Influenced_CP=="Periphery" ~ "Core \u2192 Periphery",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Core" ~ "Periphery \u2192 Core",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Periphery" ~ "Periphery \u2192 Periphery",
                                   TRUE ~ "Error")) %>%
    
    # Attempt 2
    dplyr::group_by(Year)%>%
    dplyr::mutate(Relative_Influence_Dyad = scale(Discursive_Influence) - scale(Attributional_Influence)) %>%
    #dplyr::mutate(Relative_Influence_Dyad = 0.01*Relative_Influence_Dyad) %>%
    ungroup()%>%
    
    dplyr::group_by(Dyad,Year)%>%
    dplyr::summarise(Relative_Influence_Mean = mean(Relative_Influence_Dyad,na.rm=T),
                     Relative_Influence_SE = sd(Relative_Influence_Dyad)/sqrt(length(Relative_Influence_Dyad))) %>%
  
    ggplot(data=.,
           aes(x=Year,y=Relative_Influence_Mean))+
    geom_point(size=2)+
    geom_ribbon(aes(ymax = Relative_Influence_Mean+Relative_Influence_SE,
                    ymin = Relative_Influence_Mean-Relative_Influence_SE),
                alpha=0.25,
                show.legend = F)+ 
    geom_hline(yintercept = 0, linetype = "dashed") + 
    annotate("text", x = 2000, y = 0.1, label = "Greater\nDiscursive\nInfluence",size=5)+
    annotate("text", x = 2000, y = -0.06, label = "Greater\nAttributional\nInfluence",size=5)+
    
    #stat_smooth(method = "glm")+
    #geom_smooth(method="lm")+
    stat_smooth(method = 'lm', formula = y ~ poly(x,2), 
                show.legend = F)+
    #geom_smooth(method="glm",
    #            method.args=list(family=gaussian(link="log")))+
  theme_bw()+
    ylab("Relative Influence\n(Z-Scores)")+
    theme(panel.border = element_blank(), 
          axis.line = element_line(colour = "black")) +
    theme(legend.position="bottom")+
    theme(strip.background = element_blank(), strip.placement = "outside")+
    theme(legend.background = element_rect(colour = "black")) +
    theme(legend.title=element_blank())+
    theme(strip.text.x = element_text(size = 16))+
    theme(plot.title = element_text(size=5))+
    guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
    ggpubr::stat_cor(aes(group=1),
                     method = "pearson",
                     p.accuracy = 0.001, 
                     r.accuracy = 0.01)+
    ylim(c(-0.1,0.20))+
    facet_wrap(~Dyad)

## Supplementary Information Plot | First Apperance and No Freq. Criterion --------  
  
  SI_FirstTerm_PLOT_Core_Periphery_Dyads <- Influence_SI_df %>%
    
    dplyr::mutate(Dyad = case_when(Influencer_CP=="Core" & Influenced_CP=="Core" ~ "Core \u2192 Core",
                                   Influencer_CP=="Core" & Influenced_CP=="Periphery" ~ "Core \u2192 Periphery",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Core" ~ "Periphery \u2192 Core",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Periphery" ~ "Periphery \u2192 Periphery",
                                   TRUE ~ "Error")) %>%
    
    # Attempt 2
    dplyr::group_by(Year)%>%
    dplyr::mutate(Relative_Influence_Dyad = scale(Discursive_Influence) - scale(Attributional_Influence)) %>%
    #dplyr::mutate(Relative_Influence_Dyad = 0.01*Relative_Influence_Dyad) %>%
    ungroup()%>%
    
    dplyr::group_by(Dyad,Year)%>%
    dplyr::summarise(Relative_Influence_Mean = mean(Relative_Influence_Dyad,na.rm=T),
                     Relative_Influence_SE = sd(Relative_Influence_Dyad)/sqrt(length(Relative_Influence_Dyad))) %>%

  ggplot(data=.,
         aes(x=Year,y=Relative_Influence_Mean))+
    geom_point(size=2)+
    geom_ribbon(aes(ymax = Relative_Influence_Mean+Relative_Influence_SE,
                    ymin = Relative_Influence_Mean-Relative_Influence_SE),
                alpha=0.25,
                show.legend = F)+ 
    geom_hline(yintercept = 0, linetype = "dashed") + 
    annotate("text", x = 2000, y = 0.1, label = "Greater\nDiscursive\nInfluence",size=5)+
    annotate("text", x = 2000, y = -0.06, label = "Greater\nAttributional\nInfluence",size=5)+
    
    #stat_smooth(method = "glm")+
    #geom_smooth(method="lm")+
    stat_smooth(method = 'lm', formula = y ~ poly(x,2), 
                show.legend = F)+
    #geom_smooth(method="glm",
    #            method.args=list(family=gaussian(link="log")))+
    theme_bw()+
    ylab("Relative Influence\n(Z-Scores)")+
    theme(panel.border = element_blank(), 
          axis.line = element_line(colour = "black")) +
    theme(legend.position="bottom")+
    theme(strip.background = element_blank(), strip.placement = "outside")+
    theme(legend.background = element_rect(colour = "black")) +
    theme(legend.title=element_blank())+
    theme(strip.text.x = element_text(size = 16))+
    theme(plot.title = element_text(size=5))+
    guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
    ggpubr::stat_cor(aes(group=1),
                     method = "pearson",
                     p.accuracy = 0.001, 
                     r.accuracy = 0.01)+
    ylim(c(-0.1,0.35))+
    facet_wrap(~Dyad)

  
  ## Supplementary Information Plot | Term Normalized --------  
  
  SI_TermNormed_PLOT_Core_Periphery_Dyads <- Influence_SI_TermNormed_df %>%
    
    dplyr::mutate(Dyad = case_when(Influencer_CP=="Core" & Influenced_CP=="Core" ~ "Core \u2192 Core",
                                   Influencer_CP=="Core" & Influenced_CP=="Periphery" ~ "Core \u2192 Periphery",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Core" ~ "Periphery \u2192 Core",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Periphery" ~ "Periphery \u2192 Periphery",
                                   TRUE ~ "Error")) %>%
    
    # Attempt 2
    dplyr::group_by(Year)%>%
    dplyr::mutate(Relative_Influence_Dyad = scale(Discursive_Influence) - scale(Attributional_Influence)) %>%
    #dplyr::mutate(Relative_Influence_Dyad = 0.01*Relative_Influence_Dyad) %>%
    ungroup()%>%
    
    dplyr::group_by(Dyad,Year)%>%
    dplyr::summarise(Relative_Influence_Mean = mean(Relative_Influence_Dyad,na.rm=T),
                     Relative_Influence_SE = sd(Relative_Influence_Dyad)/sqrt(length(Relative_Influence_Dyad))) %>%
    
  
  ggplot(data=.,
         aes(x=Year,y=Relative_Influence_Mean))+
    geom_point(size=2)+
    geom_ribbon(aes(ymax = Relative_Influence_Mean+Relative_Influence_SE,
                    ymin = Relative_Influence_Mean-Relative_Influence_SE),
                alpha=0.25,
                show.legend = F)+ 
    geom_hline(yintercept = 0, linetype = "dashed") + 
    annotate("text", x = 2000, y = 0.1, label = "Greater\nDiscursive\nInfluence",size=5)+
    annotate("text", x = 2000, y = -0.06, label = "Greater\nAttributional\nInfluence",size=5)+
    
    #stat_smooth(method = "glm")+
    #geom_smooth(method="lm")+
    stat_smooth(method = 'lm', formula = y ~ poly(x,2), 
                show.legend = F)+
    #geom_smooth(method="glm",
    #            method.args=list(family=gaussian(link="log")))+
    theme_bw()+
    ylab("Relative Influence\n(Z-Scores)")+
    theme(panel.border = element_blank(), 
          axis.line = element_line(colour = "black")) +
    theme(legend.position="bottom")+
    theme(strip.background = element_blank(), strip.placement = "outside")+
    theme(legend.background = element_rect(colour = "black")) +
    theme(legend.title=element_blank())+
    theme(strip.text.x = element_text(size = 16))+
    theme(plot.title = element_text(size=5))+
    guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
    ggpubr::stat_cor(aes(group=1),
                     method = "pearson",
                     p.accuracy = 0.001, 
                     r.accuracy = 0.01)+
    ylim(c(-0.1,0.15))+
    facet_wrap(~Dyad)
  
## Supplementary Information Plot | Domestic Authors Only --------  
  
  SI_Domestic_PLOT_Core_Periphery_Dyads <- SI_Domestic_Influence_df %>%
    
    dplyr::mutate(Dyad = case_when(Influencer_CP=="Core" & Influenced_CP=="Core" ~ "Core \u2192 Core",
                                   Influencer_CP=="Core" & Influenced_CP=="Periphery" ~ "Core \u2192 Periphery",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Core" ~ "Periphery \u2192 Core",
                                   Influencer_CP=="Periphery" & Influenced_CP=="Periphery" ~ "Periphery \u2192 Periphery",
                                   TRUE ~ "Error")) %>%
    
    # Attempt 2
    dplyr::group_by(Year)%>%
    dplyr::mutate(Relative_Influence_Dyad = scale(Discursive_Influence) - scale(Attributional_Influence)) %>%
    #dplyr::mutate(Relative_Influence_Dyad = 0.01*Relative_Influence_Dyad) %>%
    ungroup()%>%
    
    dplyr::group_by(Dyad,Year)%>%
    dplyr::summarise(Relative_Influence_Mean = mean(Relative_Influence_Dyad,na.rm=T),
                     Relative_Influence_SE = sd(Relative_Influence_Dyad)/sqrt(length(Relative_Influence_Dyad))) %>%
    
    
    ggplot(data=.,
           aes(x=Year,y=Relative_Influence_Mean))+
    geom_point(size=2)+
    geom_ribbon(aes(ymax = Relative_Influence_Mean+Relative_Influence_SE,
                    ymin = Relative_Influence_Mean-Relative_Influence_SE),
                alpha=0.25,
                show.legend = F)+ 
    geom_hline(yintercept = 0, linetype = "dashed") + 
    annotate("text", x = 2000, y = 0.25, label = "Greater\nDiscursive\nInfluence",size=5)+
    annotate("text", x = 2000, y = -0.15, label = "Greater\nAttributional\nInfluence",size=5)+
    
    #stat_smooth(method = "glm")+
    #geom_smooth(method="lm")+
    stat_smooth(method = 'lm', formula = y ~ poly(x,2), 
                show.legend = F)+
    #geom_smooth(method="glm",
    #            method.args=list(family=gaussian(link="log")))+
    theme_bw()+
    ylab("Relative Influence\n(Z-Scores)")+
    theme(panel.border = element_blank(), 
          axis.line = element_line(colour = "black")) +
    theme(legend.position="bottom")+
    theme(strip.background = element_blank(), strip.placement = "outside")+
    theme(legend.background = element_rect(colour = "black")) +
    theme(legend.title=element_blank())+
    theme(strip.text.x = element_text(size = 16))+
    theme(plot.title = element_text(size=5))+
    guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
    ggpubr::stat_cor(aes(group=1),
                     method = "pearson",
                     p.accuracy = 0.001, 
                     r.accuracy = 0.01)+
    ylim(c(-0.25,0.40))+
    facet_wrap(~Dyad)
  
## Plot | Relative Influence Network of Countries ---------


  International_Edgelist_df <- Influence_df %>%
    dplyr::mutate(Time_Period = case_when(Year>=1990 & Year<=2002 ~ "1990-2002",
                                          Year>=2003 & Year<=2013 ~ "2003-2013",
                                          TRUE ~ NA))%>%
    subset(is.na(Time_Period)==F) %>%
    
    # Attempt 2
    dplyr::group_by(Time_Period,Year)%>%
    dplyr::mutate(Relative_Influence_Dyad = scale(Discursive_Influence) - scale(Attributional_Influence)) %>%
    select(Time_Period,Year,Influencer_CP, Influencer,Influenced_CP,Influenced,Relative_Influence_Dyad) %>%
    subset(Year %in% c(1990,2001,2013)) %>%
    merge(.,ISO_Region_df%>%
            rename(Influencer_Region=UNREGION1,Influencer=ISO2),
          by=c("Influencer"))%>%
    merge(.,ISO_Region_df%>%
            rename(Influenced_Region=UNREGION1,Influenced=ISO2),
          by=c("Influenced"))%>%
    dplyr::group_by(Year,Influencer_Region,Influenced_Region)%>%
    dplyr::summarise(Relative_Influence_Dyad = mean(Relative_Influence_Dyad,na.rm=T))%>%
    as.data.frame()

## Table | Countries per Region -----------
  
  Table_Region_Country_df <- ISO_Region_df %>%
    merge(.,raster::ccodes()%>%select(ISO2,NAME_FAO),by=c("ISO2"))%>%
    tidyr::drop_na() %>%
    dplyr::group_by(UNREGION1)%>%
    dplyr::summarise(Name = paste(NAME_FAO,collapse=" | ")) %>%
    rename(Region=UNREGION1,Country=Name) %>%
    as.data.frame()
  
## Output | Table Countries per Region ----------  
  write.csv(Table_Region_Country_df,"/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/OUTPUT_R_Countries_per_Region_Table_Data_2024_03_19.csv",row.names = F)
  
  # vertex_information_df <- International_Edgelist_df %>%
  #   select(Influencer,Influencer_CP) %>%
  #   rename(Country=Influencer,Core_Periphery=Influencer_CP) %>%
  #   rbind(.,International_Edgelist_df %>%
  #       select(Influenced,Influenced_CP) %>%
  #         rename(Country=Influenced,Core_Periphery=Influenced_CP)) %>%
  #   unique()
  
# N.B., start for loop with 2013 to set the order the same for 2001 and 2013
for(year_ in c(2013,2001)){
  
  g <- graph_from_data_frame(International_Edgelist_df%>%
                               subset(Year==year_)%>%
                               select(Influencer_Region,
                                      Influenced_Region,
                                      Relative_Influence_Dyad) %>%
                               rename(weight=Relative_Influence_Dyad), 
                             directed = TRUE, 
                             vertices = NULL)  
  
  # get edgelist
  edgelist = get.edgelist(g)
  
  # get vertex labels
  g <- set_vertex_attr(g,"label",value=V(g)$name)
  vlabels = vertex_attr(g, "label")
  
  # get vertex groups
  #g <- set_vertex_attr(g,"group",value=V(g)$Core_Periphery)
  #vgroups = vertex_attr(g, "group")
  
  # get vertex fill color
  vfill = vertex_attr(g, "fill")
  
  # get vertex border color
  vborders = vertex_attr(g, "border")
  
  # get vertex degree
  # N.B., start for loop with 2013 to set the order the same for 2001 and 2013
  if(year_==2013){degrees = strength(g)}
  
  # get edges value
  values = edge_attr(g, "weight")
  
  # data frame with vgroups, degree, vlabels and ind
  x = data.frame(degrees, vlabels, ind=1:vcount(g))
  
  # arranging by vgroups and degrees
  #y = arrange(x, desc(degrees))
  y = arrange(x, -desc(degrees))
  

  core_regions <- c("United\nStates","Core\nCW","Core\nEurope","Core\nAsia","China")

  color.arc_match <- case_when(E(g)$weight>=0 ~ "forestgreen",#darkgreen
                               T ~ "firebrick") #orange
  color.names_match <- case_when(vlabels %in% core_regions ~ "blue",
                                 T ~ "red")
  
  # get ordering 'ind'
  new_ord = y$ind
  
pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_F_Relative_Influence_Regional_Arcs_",as.character(year_),".pdf",sep=""),
    width=(10*1), 
    height=10*1,onefile=F)
  arcplot(edgelist, 
          ordering=new_ord, 
          lwd.arcs = case_when(E(g)$weight>=0 ~ 20*E(g)$weight,
                               T ~ -20*E(g)$weight),
          alpha = 0.4,
          labels=vlabels, 
          cex.labels=1,
          show.nodes=F, 
          show.labels=T,
          col.labels = color.names_match,
          horizontal = F,
          above = case_when(E(g)$weight>=0 ~ T,
                            T ~ F),
          col.arcs = color.arc_match,
          col.nodes = vborders, 
          bg.nodes = vfill,
          cex.nodes = degrees, 
          pch.nodes = 21,
          lwd.nodes = 2, 
          outer = F, 
          line=-0.4)+ #line = -0.5
    text(0, 1.02, year_, cex=4)+
    text(0.25, 1, "Greater\nDiscursive\nInfluence", cex=1.5)+ #(x,y,name) (0.05,0.4) middle
    text(-0.25, 1, "Greater\nAttributional\nInfluence", cex=1.5) #(0.05,-0.4)
dev.off()
} # End For Loop Year
  

  
## Plot | Heatmap -------
  
  Heatmap_Influence_df <- Influence_df %>%
    
    merge(.,ISO_Region_df%>%
            rename(Influencer_Region=UNREGION1,Influencer=ISO2),
          by=c("Influencer"))%>%
    merge(.,ISO_Region_df%>%
            rename(Influenced_Region=UNREGION1,Influenced=ISO2),
          by=c("Influenced"))%>%

    mutate(Time_Period = case_when(Year%in%c(2001,2013)~Year,
                                   TRUE ~ NA))%>%
    subset(is.na(Time_Period)==F) %>%
    
    dplyr::group_by(Influencer_Region,Influenced_Region,Time_Period)%>%
    dplyr::summarise(Relative_Influence_Mean = mean(Relative_Influence,na.rm=T),
                     Relative_Influence_SE = sd(Relative_Influence,na.rm=T)/sqrt(length(Relative_Influence)),
                     N=length(Relative_Influence)) %>%
    
    as.data.frame() %>%
    arrange(Influencer_Region)%>%
    
    mutate(Influencer_Region=factor(Influencer_Region,levels=c("United\nStates","China","Core\nCW","Core\nEurope","Core\nAsia","Periphery\nEurope","Periphery\nAsia","Latin\nAmerica","Africa","Oceania"))) %>%
    mutate(Influenced_Region=factor(Influenced_Region,levels=c("United\nStates","China","Core\nCW","Core\nEurope","Core\nAsia","Periphery\nEurope","Periphery\nAsia","Latin\nAmerica","Africa","Oceania"))) %>%
    mutate(Relative_Influence_Groups = cut(Relative_Influence_Mean,
                                           breaks = c(-Inf,-0.06,0, 0.06,Inf))) %>%
    mutate(Influencer_Region_Color = case_when(Influencer_Region %in% core_regions ~ "red",
                                               T ~ "blue")) %>%
    mutate(Influenced_Region_Color = case_when(Influenced_Region %in% core_regions ~ "red",
                                               T ~ "blue")) %>%
    tidyr::complete(.,Influencer_Region,Influenced_Region,Time_Period)
  
  # Note - This creates the red/blue color of the region names.
  # N.B., this will pass in a warning.
  # https://stackoverflow.com/questions/38862303/customize-ggplot2-axis-labels-with-different-colors
  x_color <- ifelse(unique(Heatmap_Influence_df$Influenced_Region) %in% core_regions, "red", "blue")
  y_color <- rev(ifelse(unique(Heatmap_Influence_df$Influencer_Region) %in% core_regions, "red", "blue"))
  
  
  PLOT_Regional_Dyad_Heatmap <- ggplot(data=Heatmap_Influence_df,
                                       aes(y=Influencer_Region,
                                           x=Influenced_Region,
                                           fill=Relative_Influence_Groups)) +
    geom_tile(color = "black",
              #aes(fill=Relative_Influence_Mean),
              lwd = 0.25,
              linetype = 1)+
    ylab("Influencer")+
    xlab("Influenced")+
    theme_bw()+

    geom_label(data=.%>%subset(abs(Relative_Influence_Mean)>=0.06),
               aes(label = paste(sprintf("%0.2f",round(Relative_Influence_Mean, digits = 2)),"\n","(",sprintf("%0.2f",round(Relative_Influence_SE, digits = 2)),")","\n","N = ",N,sep="") ), 
               fill="white", 
               colour = "black", 
               size = 3) +
    
    scale_fill_manual(name = "Relative\nInfluence\n(Z-Scores)",
                      breaks = levels(Heatmap_Influence_df$Relative_Influence_Groups),
                      #values= c("brown","orange","green","darkgreen"),
                      values= c("firebrick","indianred1","yellowgreen","forestgreen"),
                      na.value = 'grey')+
    scale_y_discrete(limits=rev)+
    theme(strip.text.x = element_text(size = 20))+
    theme(panel.border = element_blank(),
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          axis.line = element_blank()) +
    theme(legend.position="bottom")+
    theme(strip.background = element_blank(), strip.placement = "outside")+
    theme(legend.background = element_rect(colour = "black"))+
    theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1, colour=x_color))+
    theme(axis.text.y = element_text(colour=y_color))+
    facet_wrap(~Time_Period)
  
# Main Figures ---------
  
pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_A_Descriptive_Country_Paper_Percent_Hexgram_and_Histograms.pdf",sep=""),width=(8*1.75), height=8,onefile=F)
ggpubr::ggarrange(PLOT_Percent_Papers_by_Country,
                    PLOT_Descriptive_Stats,
                    labels=c("(a)","(b)"),
                    nrow = 1, 
                    common.legend = F)
dev.off()

pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_B_QAP.pdf",sep=""),width=(8*1), height=8,onefile=F)
PLOT_QAP
dev.off()


pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_C_Gini_Centrality.pdf",sep=""),width=(9*1), height=9,
    onefile=F)
ggpubr::ggarrange(
                ggpubr::ggarrange(PLOT_Gini_Attributional_Influence,PLOT_Gini_Discursive_Influence,
                  labels=c("(a)","(b)"),
                  common.legend = F),
                  PLOT_Influence_Centrality,
                  labels=c("","(c)"),
                  nrow=2,
                  common.legend = F)
dev.off()


pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_D_Relative_Influence_Gini_Centrality.pdf",sep=""),width=(8*1.8), height=8,onefile=F)
ggpubr::ggarrange(PLOT_Gini_Relative_Influence,
                  PLOT_Relative_Influence_CorePeriphey,
                      labels=c("(a)","(b)"),
                  nrow=1,
                  common.legend = F)
dev.off()



cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_E_Regional.pdf",sep=""),width=(8*1), height=8*1,
    onefile=F,family="Arial Unicode MS")
PLOT_Core_Periphery_Dyads
dev.off()


pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_F_Regional_Dyad_Heatmaps.pdf",sep=""),width=(8*1.5), height=8,onefile=F)
ggpubr::ggarrange(PLOT_Regional_Dyad_Heatmap,
                  labels=c("(b)"),
                  nrow=1,
                  common.legend = F)
dev.off()



cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/SI_FirstTerm_FIGURE_Regional.pdf",sep=""),width=(8*1), height=8*1,
          onefile=F,family="Arial Unicode MS")
SI_FirstTerm_PLOT_Core_Periphery_Dyads
dev.off()

cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/SI_TermNormed_FIGURE_Regional.pdf",sep=""),width=(8*1), height=8*1,
          onefile=F,family="Arial Unicode MS")
SI_TermNormed_PLOT_Core_Periphery_Dyads
dev.off()


cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/SI_Domestic_FIGURE_Regional.pdf",sep=""),width=(8*1), height=8*1,
          onefile=F,family="Arial Unicode MS")
SI_Domestic_PLOT_Core_Periphery_Dyads
dev.off()

# RR1 | Analyses and Figures -------
## RR1 - Plot | Percent of Terms Across or Within Regions ----------

PLOT_RR1_Regional_Percent <- Discursive_Influence_Raw_df %>%
  merge(.,ISO_Region_df,by.y=c("ISO2"),by.x=c("Influencer")) %>%
  rename(Influencer_Region = UNREGION1) %>%
  merge(.,ISO_Region_df,by.y=c("ISO2"),by.x=c("Influenced")) %>%
  rename(Influenced_Region = UNREGION1) %>%
  select(-c(Influenced,Influencer)) %>%
  mutate(Same_Region = ifelse(Influencer_Region==Influenced_Region,"Within Region","Across Regions")) %>%
  group_by(Year,Same_Region) %>%
  summarize(N=n()) %>%
  group_by(Year)%>%
  mutate(Percent = N/sum(N)) %>%
  as.data.frame() %>%
  tidyr::drop_na() %>%
  ggplot(data=.,aes(x=Year,y=Percent,group=Same_Region))+
  geom_point(size=4,
             aes(colour=Same_Region))+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left",
                   aes(colour=Same_Region))+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Discursive Influence\nPercent of Terms Moving across or within Regions")+
  xlab("Year")+
  geom_smooth(show.legend = F, method="lm",
              aes(group=Same_Region,
                  colour=Same_Region))+
  scale_y_continuous(labels = scales::percent)+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_uchicago()

## RR1 - Plot | Percent of Terms Across or Within Regions By Regions----------

Discursive_Influence_Raw_df %>%
  merge(.,ISO_Region_df,by.y=c("ISO2"),by.x=c("Influencer")) %>%
  rename(Influencer_Region = UNREGION1) %>%
  merge(.,ISO_Region_df,by.y=c("ISO2"),by.x=c("Influenced")) %>%
  rename(Influenced_Region = UNREGION1) %>%
  mutate(CP_Influencer = ifelse(Influencer %in% Core_Country,"Core","Periphery")) %>%
  mutate(CP_Influenced = ifelse(Influenced %in% Core_Country,"Core","Periphery")) %>%
  mutate(Same_Region = ifelse(Influencer_Region==Influenced_Region,"Within Region","Across Regions")) %>%
  select(-c(Influenced,Influencer)) %>%
  group_by(Year,Same_Region,Influenced_Region) %>%
  summarize(N=n()) %>%
  group_by(Year,Influenced_Region)%>%
  mutate(Percent = N/sum(N)) %>%
  as.data.frame() %>%
  tidyr::drop_na() %>%
  subset(Year>=2000)%>%
  ggplot(data=.,aes(x=Year,y=Percent,group=Same_Region))+
  geom_point(size=4,
             aes(colour=Same_Region))+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left",
                   aes(colour=Same_Region))+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Discursive Influence\nPercent of Terms Moving across or within Regions")+
  xlab("Year")+
  scale_y_continuous(labels = scales::percent)+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_aaas()+
  facet_wrap(~Influenced_Region,scales = "free_y")


## RR1 - Plot | Periphery Terms - Periphery Only Adoption  -----

core_regions <- c("United\nStates","Core\nCW","Core\nEurope","Core\nAsia","China")

Majority_Periphery_Terms <- Discursive_Influence_Raw_df %>%
  
  # merge(.,ISO_Region_df,by.y=c("ISO2"),by.x=c("Influencer")) %>%
  # rename(Influencer_Region = UNREGION1) %>%
  # merge(.,ISO_Region_df,by.y=c("ISO2"),by.x=c("Influenced")) %>%
  # rename(Influenced_Region = UNREGION1) %>%
  # select(-c(Influenced,Influencer)) %>%
  # mutate(Same_Region = ifelse(Influencer_Region==Influenced_Region,"Same_Region","Different")) %>%
  
  mutate(CP_Influenced = case_when(Influenced %in% Core_Country ~ "Core",
                    TRUE ~ "Periphery"))%>%
  subset(Year>=1990) %>%
  select(Term,Influenced,CP_Influenced) %>%
  group_by(Term,CP_Influenced) %>%
  summarize(Count = n()) %>%
  group_by(Term) %>%
  mutate(Percent = Count/sum(Count)) %>%
  as.data.frame() %>%
  
  #If a term is ONLY adopted by Periphery Countries (100%) observed time period
  subset(Percent==1 & CP_Influenced=="Periphery") %>%
  select(Term) %>%
  mutate(Term_Type = "Terms Only Adopted\nby Periphery Countries")

Non_Majority_Periphery_Terms <-  data.frame(Term = setdiff(unique(Discursive_Influence_Raw_df$Term),Majority_Periphery_Terms$Term)) %>%
  mutate(Term_Type = "All Other Terms")


### Dyads Plot -------

# Number of Periphery Adopted Only Terms
# dim(Majority_Periphery_Terms)[1]

Periphery_Adopted_Terms_RI_df <- Discursive_Influence_Raw_df %>%
  subset(Year>=1990)%>% 
  merge(.,rbind(Majority_Periphery_Terms,Non_Majority_Periphery_Terms) %>% select("Term","Term_Type"),
        by=c("Term"),all.y = T) %>%
  merge(.,Attributional_Influence_Raw_df,
        by=c("Influencer","Influenced","Year","Term"),
        all.x=T)%>%
  replace(is.na(.), 0) %>%
  subset(Influencer!=Influenced) %>%
  arrange(Year) %>%
  
  dplyr::group_by(Year,Influencer,Influenced,Term_Type) %>%
  dplyr::summarise(Discursive_Influence = sum(Weight),
                   Attributional_Influence = sum(Influenced_Weights))%>%
  
  dplyr::group_by(Year) %>%
  dplyr::mutate(DI_Scale = scale(Discursive_Influence),
                AI_Scale = scale(Attributional_Influence)) %>%
  ungroup()%>%
  dplyr::mutate(Relative_Influence = DI_Scale-AI_Scale)%>%
  
  mutate(Sender_Core_Periphery = case_when(Influencer%in%Core_Country~"Core",
                                           TRUE ~ "Periphery"))%>%
  mutate(Receiver_Core_Periphery = case_when(Influenced%in%Core_Country~"Core",
                                             TRUE ~ "Periphery"))%>%
  mutate(CP_Dyad = paste(Sender_Core_Periphery,"\u2192",Receiver_Core_Periphery)) %>%
  
  group_by(Year,CP_Dyad,Term_Type)%>%
  summarize(Centrality=mean(Relative_Influence,na.rm=T),
            SE = sd(Relative_Influence)/sqrt(length(Relative_Influence))) %>%
  as.data.frame()

PLOT_RR1_Periphery_Only_Terms_Dyads <-Periphery_Adopted_Terms_RI_df %>%
  
  #Remove Core as Receiver when looking at exclusive periphery terms
  subset(CP_Dyad!="Core → Core" & CP_Dyad!="Periphery → Core") %>%
  
  ggplot(data=.,aes(x=Year,y=Centrality,group=Term_Type))+
  geom_point(size=4,
             aes(group=Term_Type,
                 colour=Term_Type))+
  geom_ribbon(aes(ymin=Centrality-SE,
                  ymax=Centrality+SE,
                  colour = Term_Type,
                  group = Term_Type),
              alpha=0.25,
              show.legend = F)+
  geom_hline(yintercept = 0,linetype="dashed")+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left",
                   aes(colour=Term_Type))+
  stat_smooth(method='lm',formula = y ~ x, 
              show.legend = F, aes(colour=Term_Type))+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Relative Influence\n(Z-Scores)")+
  xlab("Year")+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_jco()+
  theme(strip.text.x = element_text(size = 16))+
  facet_wrap(~CP_Dyad)

## RR1 - Output | All Terms -----
# write.csv(Discursive_Influence_Raw_df %>%
#             subset(Year>=1990) %>%
#             select(Term) %>%
#             unique(),"/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/ ",
#           row.names = F)

# ChatGPT - Prompt 
# Upload the CSV with all terms
"This is a long list of n-grams of scientific terms. Of these terms, I'm trying to identify those terms that are indigenous or regional or national in its focus. Go through the list and create a new list that satisfies these criteria, and create a new CSV. One column should be the term that satisfies this criterion and another column should refer to the country it refers to (whether locally or nationally).

First, replace the full country names with their ISO2 codes and create new rows for terms associated with multiple countries; second, ensure that 'African American' was specifically mapped to the US; and finally, add a 'Status' column classifying each country as either 'Core' or 'Periphery' based on the provided list below."

## RR1 - Plot | Periphery Terms - Periphery-Referenced Term  -----

Regional_Indigenous_Terms <- read.csv("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/Regional_and_Local_Scientific_Terms_-_Complete_List_LATEST.csv") %>%
  subset(Status == "Periphery")%>%
  select(Term)%>%
  unique() %>%
  mutate(Term_Type = "Periphery-Referenced Terms Only")

### Dyads Plot -------

# Number of Terms that are Periphery-Referenced
# dim(Regional_Indigenous_Terms)[1]

Non_Regional_Indigenous_Terms <-  data.frame(Term = setdiff(unique(Discursive_Influence_Raw_df$Term),Regional_Indigenous_Terms$Term)) %>%
  mutate(Term_Type = "All Other Terms")

Periphery_Referenced_Terms_RI_df <- Discursive_Influence_Raw_df %>%
  subset(Year>=1990)%>% 
  merge(.,rbind(Regional_Indigenous_Terms,Non_Regional_Indigenous_Terms) %>% select("Term","Term_Type"),
        by=c("Term"),all.y = T) %>%
  merge(.,Attributional_Influence_Raw_df,
      by=c("Influencer","Influenced","Year","Term"),
      all.x=T)%>%
  replace(is.na(.), 0) %>%
  subset(Influencer!=Influenced) %>%
  arrange(Year) %>%
  
  dplyr::group_by(Year,Influencer,Influenced,Term_Type) %>%
  dplyr::summarise(Discursive_Influence = sum(Weight),
                   Attributional_Influence = sum(Influenced_Weights))%>%
  
  dplyr::group_by(Year) %>%
  dplyr::mutate(DI_Scale = scale(Discursive_Influence),
                AI_Scale = scale(Attributional_Influence)) %>%
  ungroup()%>%
  dplyr::mutate(Relative_Influence = DI_Scale-AI_Scale)%>%
  
  mutate(Sender_Core_Periphery = case_when(Influencer%in%Core_Country~"Core",
                                           TRUE ~ "Periphery"))%>%
  mutate(Receiver_Core_Periphery = case_when(Influenced%in%Core_Country~"Core",
                                             TRUE ~ "Periphery"))%>%
  mutate(CP_Dyad = paste(Sender_Core_Periphery,"\u2192",Receiver_Core_Periphery)) %>%
  
  group_by(Year,CP_Dyad,Term_Type)%>%
  summarize(Centrality=mean(Relative_Influence,na.rm=T),
            SE = sd(Relative_Influence)/sqrt(length(Relative_Influence))) %>%
  as.data.frame()


PLOT_RR1_Periphery_Referenced_Terms_Dyads <- Periphery_Referenced_Terms_RI_df%>%

  ggplot(data=.,aes(x=Year,y=Centrality,group=Term_Type))+
  geom_point(size=4,
             aes(group=Term_Type,
                 colour=Term_Type))+
  geom_ribbon(aes(ymin=Centrality-SE,
                  ymax=Centrality+SE,
                  colour = Term_Type,
                  group = Term_Type),
              alpha=0.25,
              show.legend = F)+
  geom_smooth(show.legend = F, method="lm", aes(colour=Term_Type))+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left",
                   aes(colour=Term_Type))+
  geom_hline(yintercept = 0,linetype="dashed")+
  #stat_smooth(method='lm',formula = y ~ poly(x,4), 
  #            show.legend = F, aes(colour=Term_Type))+
  theme_bw()+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Relative Influence\n(Z-Scores)")+
  xlab("Year")+
  theme(strip.text.x = element_text(size = 16))+
  theme(plot.title = element_text(size=5))+
  scale_x_continuous(breaks= scales::pretty_breaks())+
  ggsci::scale_color_jco()+
  facet_wrap(~CP_Dyad)

## RR1 - Plot | National Signature Replacement ------

national_signatures_df <- read.csv("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Data/OUTPUT_Python_HNB_RR1_National_Signature_Influence_2024_03_19.csv")

PLOT_RR1_National_Signatures <- national_signatures_df %>% 
  subset(Influence_1!=1) %>%
  dplyr::group_by(Sender_Core_Periphery,Receiver_Core_Periphery,Year)%>%
  summarize(Influence_1_Mean = mean(Influence_1,na.rm=T),
            Influence_1_SE = sd(Influence_1,na.rm=T)/sqrt(length(Influence_1)))%>%
  mutate(CP_Dyad = paste(Sender_Core_Periphery,"\u2192",Receiver_Core_Periphery)) %>%

  mutate(CP_Dyad = case_when(Sender_Core_Periphery == "Core" & Receiver_Core_Periphery=="Core" ~ "Core Mimicks Core\nin the Past\n(Core \u2192 Core)",
                             Sender_Core_Periphery == "Core" & Receiver_Core_Periphery=="Periphery" ~ "Periphery Mimicks Core\nin the Past\n(Core \u2192 Periphery)",
                             Sender_Core_Periphery == "Periphery" & Receiver_Core_Periphery=="Core" ~ "Core Mimicks Periphery\nin the Past\n(Periphery \u2192 Core)",
                             Sender_Core_Periphery == "Periphery" & Receiver_Core_Periphery=="Periphery" ~ "Periphery Mimicks Periphery\nin the Past\n(Periphery \u2192 Periphery)",
                             TRUE ~ "Error"))%>%
  mutate(CP_Dyad = factor(CP_Dyad,levels=c("Core Mimicks Core\nin the Past\n(Core \u2192 Core)",
                                           "Periphery Mimicks Core\nin the Past\n(Core \u2192 Periphery)",
                                           "Core Mimicks Periphery\nin the Past\n(Periphery \u2192 Core)",
                                           "Periphery Mimicks Periphery\nin the Past\n(Periphery \u2192 Periphery)")))%>%
  as.data.frame() %>%
  ggplot(data=.,
         aes(x=Year,y=Influence_1_Mean,group=CP_Dyad))+
  geom_point(aes(colour=CP_Dyad))+
  #geom_smooth(method="lm")+
  theme_bw()+
  ggpubr::stat_cor(method = "pearson",
                   p.accuracy = 0.001,
                   r.accuracy = 0.01,
                   label.y.npc="top",
                   label.x.npc = "left")+
  geom_ribbon(aes(ymin=Influence_1_Mean-Influence_1_SE,
                  ymax=Influence_1_Mean+Influence_1_SE,
                  group = CP_Dyad),
              alpha=0.25,
              show.legend = F)+
  theme(panel.border = element_blank(), 
        axis.line = element_line(colour = "black")) +
  theme(legend.position = "bottom")+
  theme(strip.background = element_blank(), strip.placement = "outside")+
  theme(legend.background = element_rect(colour = "black")) +
  theme(legend.title=element_blank())+
  guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4)))+
  ylab("Mimickry\n(Cosine Similarity)")+
  xlab("Year")+
  theme(strip.text.x = element_text(size = 16))+
  theme(plot.title = element_text(size=5))+
  geom_point(size=2)+
  theme(legend.position="none")+
  ggsci::scale_color_aaas()+
  geom_smooth(show.legend = F, method="lm")+
  facet_wrap(~CP_Dyad)

# RR1 | Final Figures ------


cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_RR1_Periphery_Only_Terms_Dyads.pdf",sep=""),width=(8*1.5), height=8*1,onefile=F)
PLOT_RR1_Periphery_Only_Terms_Dyads
dev.off()

cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_RR1_Periphery_Referenced_Terms_Dyads.pdf",sep=""),width=(8), height=8*1,onefile=F)
PLOT_RR1_Periphery_Referenced_Terms_Dyads
dev.off()

cairo_pdf(paste("/Users/cjgomez/Library/CloudStorage/Box-Box/PROJECT_Phoenix/Figures/Figures_Data_2024_03_19/FIGURE_RR1_National_Signatures.pdf",sep=""),width=(8*1), height=8*1,onefile=F,family="Arial Unicode MS")
PLOT_RR1_National_Signatures
dev.off()
