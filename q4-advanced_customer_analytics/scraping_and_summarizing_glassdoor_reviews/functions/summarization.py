#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
from fpdf import FPDF

# ------------------------------------------------------------------------------
# Summarize reviews into text using OpenAI's GPT-3 model
# ------------------------------------------------------------------------------

def openai_tldr_summarization(text:str):
    """

    Parameters
    ----------
    text : str
        All the reviews joined in a single string.

    Returns
    -------
    summary : str
        A summary of all the reviews.

    """
    
    # API key
    OPENAI_API_KEY = ('XXXXXXXXXX')
    openai.api_key = OPENAI_API_KEY
    
    # append some string to the text
    # to help the model understand which application we want to use
    text = text + 'Tl;dr'
    
    # send the request
    response = openai.Completion.create(model="text-davinci-002",
                                        prompt=text,
                                        temperature=0.8,
                                        max_tokens=65,
                                        top_p=1.0,
                                        frequency_penalty=0.0,
                                        presence_penalty=0.9
                                        )
    
    # get the response
    summary = response['choices'][0]['text']
    
    return summary

# ------------------------------------------------------------------------------
# Grammar corrections using OpenAI's GPT-3 model
# ------------------------------------------------------------------------------

def openai_grammar_correction(text:str):
    """

    Parameters
    ----------
    text : str
        All the reviews joined in a single string.

    Returns
    -------
    summary : str
        A summary of all the reviews.

    """
    
    # API key
    OPENAI_API_KEY = ('XXXXXXXXXX')
    openai.api_key = OPENAI_API_KEY
    
    # append some string to the text
    # to help the model understand which application we want to use
    text = 'Correct this to standard English:' + text
    
    # send the request
    response = openai.Completion.create(model="text-davinci-002",
                                        prompt=text,
                                        temperature=0.0,
                                        max_tokens=65,
                                        top_p=1.0,
                                        frequency_penalty=0.0,
                                        presence_penalty=0.0
                                        )
    
    # get the response
    output = response['choices'][0]['text']
    
    return output

# ------------------------------------------------------------------------------
# Grammar corrections using OpenAI's GPT-3 model
# ------------------------------------------------------------------------------

def create_pdf_report(no_reviews:int,
                      avg_rating:float,
                      summary_pros:str,
                      summary_cons:str):
    """
    
    Parameters
    ----------
    no_reviews : int
        The total number of reviews available.
    avg_rating : float
        The average rating.
    summary_pros : str
        The summary of all the pros obtained from the GPT-3 model.
    summary_cons : str
        The summary of all the cons obtained from the GPT-3 model.

    Returns
    -------
    None.

    """
    
    # https://pyfpdf.readthedocs.io/en/latest/
    pdf = FPDF(format='A3', orientation='L')
    pdf.add_page()
    
    # left banner
    pdf.set_fill_color(r=0, g=0, b=0)
    pdf.rect(x=0, y=0, w=100, h=297, style='DF')
    
    # glassdoor logo
    pdf.image('./images/glassdoor.png', x=10, y=0, w=80, h=0, type='PNG', link='')
    
    # text
    pdf.set_text_color(r=255, g=255, b=255)
    pdf.set_xy(x=10, y=50)
    pdf.set_font('Courier', 'B', 16)
    pdf.multi_cell(w=80, h=10, txt='Is Data Scientist still the sexiest job of the 21st century? Or at least in Amazon...', border=0, align='C')

    # company
    pdf.set_xy(x=0, y=120)
    pdf.set_font('Courier', 'B', 20)
    pdf.cell(w=100, h=5, txt='Company', border=0, ln=1, align='C')
    pdf.image('./images/amazon.png', x=15, y=135, w=70, h=0, type='PNG', link='')
    
    # reviews
    pdf.set_xy(x=0, y=185)
    pdf.set_font('Courier', 'B', 20)
    pdf.cell(w=100, h=5, txt='Reviews', border=0, ln=1, align='C') # 3 after the line
    pdf.set_xy(x=0, y=205)
    pdf.set_font('Courier', 'B', 60)
    pdf.cell(w=100, h=5, txt=no_reviews, border=0, ln=1, align='C')
    
    # avg rating
    pdf.set_xy(x=0, y=250)
    pdf.set_font('Courier', 'B', 20)
    pdf.cell(w=100, h=5, txt='Avg Rating', border=0, ln=1, align='C') # 3 after the line
    pdf.set_xy(x=0, y=270)
    pdf.set_font('Courier', 'B', 60)
    pdf.set_text_color(r=0, g=175, b=65)
    pdf.cell(w=100, h=5, txt=avg_rating, border=0, ln=1, align='C')
    
    # upper graphs
    pdf.image('./images/number_of_reviews_per_rating.png', x=110, y=5, w=145, h=0, type='PNG', link='')
    pdf.image('./images/number_of_reviews_and_avg_rating_per_year.png', x=265, y=5, w=145, h=0, type='PNG', link='')

    # middle line
    pdf.set_draw_color(r=0, g=175, b=65)
    pdf.line(x1=0, y1=105, x2=420, y2=105)
    
    pdf.set_text_color(r=0, g=0, b=0)

    # pros section
    pdf.image('./images/top_5_words_MOST FREQUENTLY_in_pros.png', x=110, y=110, w=85, h=0, type='PNG', link='')
    pdf.image('./images/top_5_words_ONLY_in_pros.png', x=200, y=110, w=85, h=0, type='PNG', link='')
    pdf.set_xy(x=295, y=120)
    pdf.set_font('Courier', 'BI', 12)
    pdf.multi_cell(w=110, h=5, txt='What do people love the most?', border=0, align='J')
    pdf.set_xy(x=295, y=130)
    pdf.set_font('Courier', '', 12)
    pdf.multi_cell(w=115, h=5, txt=summary_pros, border=0, align='J')
    
    # cons section
    pdf.image('./images/top_5_words_MOST FREQUENTLY_in_cons.png', x=110, y=205, w=85, h=0, type='PNG', link='')
    pdf.image('./images/top_5_words_ONLY_in_cons.png', x=200, y=205, w=85, h=0, type='PNG', link='')
    pdf.set_xy(x=295, y=215)
    pdf.set_font('Courier', 'BI', 12)
    pdf.multi_cell(w=110, h=5, txt='What do people dislike the most?', border=0, align='J')
    pdf.set_xy(x=295, y=225)
    pdf.set_font('Courier', '', 12)
    pdf.multi_cell(w=115, h=5, txt=summary_cons, border=0, align='J')
    
    pdf.output('./summary/summary.pdf','F')