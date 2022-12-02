#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unidecode
import contractions
import re

def replace_accented_characters(review:str):
    return unidecode.unidecode(review)

def expand_contractions(review:str):
    return contractions.fix(review)

def remove_ordered_bullet_points(review:str):
    bullet_point_symbols = ['1.','1)']
    for item in bullet_point_symbols:
        review = review.replace(item,'',1).strip() if review[:2] == item else review
        review = re.sub(rf'\s+[0-9]+\{item[1]}\s+','.',review)
    return review

def remove_unordered_bullet_points(review:str):
    bullet_point_symbols = ['#','*','-','>']
    for item in bullet_point_symbols:
        review = review.replace(item,'',1).strip() if review[0] == item else review
        review = re.sub(rf'\s+\{item}\s+|\s+\{item}','.',review)
    return review

def replace_colons_with_dots(review:str):
    return review.replace(':','.')

def replace_semicolons_with_commas(review:str):
    return review.replace(';',',')

def remove_leading_trailing_spaces_from_dots(review:str):
    return re.sub(r'\s+\.\s+','.',review)

def remove_leading_trailing_spaces_from_commas(review:str):
    return re.sub(r'\s+\,\s+',',',review)

def remove_multiple_continuous_special_characters(review:str):
    return re.sub(r'[^\s\w]{2,}','.',review)

def remove_multiple_continuous_blank_spaces(review:str):
    return re.sub(r'\s{2,}',' ',review)

def remove_leftover_characters(review:str):
    return re.sub(r'[^\s\w\.\,\/\-\!]','',review)

def fix_work_life_balance_cases(review:str):
    review = review.lower().replace('work lift balance','work life balance')
    review = review.lower().replace('working life balance','work life balance')
    review = review.lower().replace('work-life balance','work life balance')
    review = review.lower().replace('work-life balanced','work life balance')
    review = review.lower().replace('work/life balance','work life balance')
    review = review.lower().replace('work/life time','work life balance')
    review = review.lower().replace('worklife balance','work life balance')
    review = review.lower().replace('wlb','work life balance')
    return review

def beautify_text(review:str):
    review = re.sub('(?<=[a-zA-Z])[,]+(?=[a-zA-z])',', ',review)
    review = re.sub('(?<=[a-zA-Z])[.]+(?=[a-zA-z])','. ',review)
    return review

def capitalize_sentences(review:str):
    return '. '.join([sentence.strip()[:1].upper() + sentence.strip()[1:] for sentence in review.split('.')]).strip()

def remove_commas_before_dots(review:str):
    return review.replace(',.','.')

def split_pros_and_cons(review:str):
    pros = review.split(' *separator* ')[0].strip()
    cons = review.split(' *separator* ')[1].strip()
    return pros, cons

def concat_pros_and_cons(pros:str, cons:str, separator=True):
    if separator: review = pros + ' *separator* ' + cons
    else: review = pros + ' ' + cons
    return review

def clean_review(review:str):
    review = replace_accented_characters(review)
    review = expand_contractions(review)
    review = remove_ordered_bullet_points(review)
    review = remove_unordered_bullet_points(review)
    review = replace_colons_with_dots(review)
    review = replace_semicolons_with_commas(review)
    review = remove_leading_trailing_spaces_from_dots(review)
    review = remove_leading_trailing_spaces_from_commas(review)
    review = remove_multiple_continuous_special_characters(review)
    review = remove_multiple_continuous_blank_spaces(review)
    review = remove_leftover_characters(review)
    review = fix_work_life_balance_cases(review)
    review = beautify_text(review)
    review = capitalize_sentences(review)
    review = remove_commas_before_dots(review)
    return review

def text_preprocessing(review:str):
    pros, cons = split_pros_and_cons(review)
    pros = clean_review(pros)
    cons = clean_review(cons)
    review = concat_pros_and_cons(pros, cons)
    return review
    