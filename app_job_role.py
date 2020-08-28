class resume_matcher:

    def input(job_role_skills, word_vect,nlp):
        import spacy
        #updated_list=updated_list.split(',')

        def wordslist_to_Matcher(words_list):
            """It will take list of words and Make a Matcher of it"""
            global nlp

            matcher = Matcher(nlp.vocab)
            words_included = []

            for word in words_list:
                if word not in words_included:
                    pattern = [{'LOWER': str(word)}]
                    # print(str(word), len(str(word)))
                    matcher.add(str(word), None, pattern)
                    words_included.append(word)

            return matcher, words_included

        def Match(matcher, doc):
            """It will give all matches in the file w.r.t to the keywords in Matcher\nArguments: Matcher, spacy.tokens.Docs\nReturns: Matched Words, Freq of matches"""
            global nlp
            key_freq = {}
            matches = matcher(doc)

            x = [match[0] for match in matches]
            y = set(x)

            for id_ in y:
                value = x.count(id_)
                # print(value, id_)
                string_id = nlp.vocab.strings[id_]
                key_freq[string_id] = value

            keys_list = list(key_freq.keys())
            return keys_list, key_freq

        def get_keywords_match(text, words_list):
            from spacy.matcher import Matcher
            global nlp
            skills_matcher, all_skill = wordslist_to_Matcher(words_list)
            # print('Keywords for matching:', len(all_skills))
            doc = nlp(text)
            skills, freq = Match(skills_matcher, doc)

            # print(freq)

            return skills, freq

        import requests
        import json
        from gensim.models.keyedvectors import KeyedVectors

        import os
        import pandas as pd

        def get_keywords(jd):
            url = "https://jobfit.perspectico.com/parser"

            input_dict = {"description": {"0": jd}, "skills": {"0": ""}}
            j = json.dumps(input_dict)
            data = {"inputFile": j}

            try:
                response = requests.post(url, data)
                result = response.json()
                # print(result)
                if result['Success']:
                    return result['Keywords']
                else:
                    print("ERROR: Keywords not fetched")
                    result = []
                    return result
            except:
                print("ERROR")
                result = []
                return result



        import pickle
        infile = open('output.pkl', 'rb')
        job_roles_icp= pickle.load(infile)
        infile.close()

        cv_name=list(job_roles_icp.keys())

        skills = {}
        percent = {}
        skills_match = {}
        percent_embedings = {}
        for i in cv_name:
            path=i
            skills.update({i:''})
            percent.update({i: []})
            skills_match.update({i: []})
            percent_embedings.update({i: []})
            print(' \n ')
            string_skills = ' '
            for j in job_roles_icp[i]['skills']:
                string_skills = string_skills + ' ' +j
            skills[i]=string_skills
            print(i,string_skills)

        def get_closest(word):

            word = word.lower()
            words = [word]
            similar_vals = [1]
            try:
                similar_list = word_vect.most_similar(word)

                for tupl in similar_list:
                    words.append(tupl[0])
                    similar_vals.append(tupl[1])
            except:

                pass

            return words, similar_vals


        def get_skills(role):
            url = "https://jobfit.perspectico.com/recommendation"

            data = {"jobRole": role}
            try:
                response = requests.post(url, data)
                result = response.json()
                return result
            except:
                pass

        print("final list of skills from api and JD")
        print(job_role_skills)
        total_skills = len(job_role_skills)
        skills_parse = {" length":len(job_role_skills) ,"skills parsed":job_role_skills}

        word_value = {}
        similar_words_needed = 3
        for word in job_role_skills:  # getting synonyms of skills from recruiter job title
            similar_words, similarity = get_closest(word)
            for i in range(len(similar_words)):
                word_value[similar_words[i]] = word_value.get(similar_words[i], 0) + similarity[i]

        all = list(word_value.keys())
        print("length of final embedings:{}  \n  ,final bucket:{}".format(len(all), all))
        final_skills = {"length of final embedings":len(all) ,"final bucket":all}


        import math
        no_of_cv = len(cv_name)

        count = {}
        idf = {}
        for word in word_value.keys():
            count[word] = 0
            for i in skills.keys():
                try:
                    if word in skills[i]:
                        count[word] += 1
                        # print("{}-{}".format(word, skills[i]))
                except:
                    pass
            if (count[word] == 0):
                count[word] = 1
            # idf[word] = math.log(no_of_cv / count[word])
        # print(idf)

        score = {}
        for i in skills.keys():
            score[i] = 0
            k = 0

            matched_skills,freq=get_keywords_match(skills[i],list(word_value.keys()))
            skills_match[i] =matched_skills
            print(matched_skills,freq)
            tf=freq
            for word in matched_skills:
                score[i] = score[i] + word_value[word] * tf[word]


            f = ((len(matched_skills) / (total_skills ) * 100))
            percent[i].append(f)
            percent_embedings[i].append(((len(matched_skills) / (len(all) * 0.10)) * 100))

        l = []
        for i in percent_embedings.values():
            l.append(i)
        l.sort(reverse=True)

        print(score)
        cosine_score = {}
        for i in score.keys():
            print("CV name:{}, score:{} \n ".format(i, score[i]))
            cosine_score.update({ i:score[i]})


        def get_key(val):
            for key, value in percent_embedings.items():
                if val == value:
                    return key

            return "key doesn't exist"

        final_result = {}
        for i in l:
            final_result.update({get_key(i): i})

        # print(final_result)
        heading4 = "\n  \n Skills Match  \n  \n"
        skillsmatch = {}
        for i in skills_match.keys():
            print(
                "CV name:{}, number of skills matched:{}, \n  skills matched:{} \n  \n ".format(i.split('/')[-1], len(skills_match[i]),
                                                                                                skills_match[i]))
            skillsmatch.update({ i.split('/')[-1] :skills_match[i] })
            #killsmatch.update({ i : len(skills_match[i]) })

        print(" \n  \n ====================percentage score===================================")
        heading5 = "\n  \n Percentage Score using Skills Recommendation Engine and Job Description \n \n"
        percentage_score = {}
        for i in percent.keys():
            print("CV name:{}, score:{} \n ".format(i.split('/')[-1], percent[i]))
            percentage_score.update({i.split('/')[-1]:percent[i]})


        print(" \n  \n ====================percentage score using word embedings===================================")
        heading6 = "\n  \nPercentage Score using Word Embedings \n \n"
        percentembedings = {}

        for i in percent_embedings.keys():
            print("CV name:{}, score:{} \n ".format(i.split('/')[-1], percent_embedings[i]))
            percentembedings.update({i.split('/')[-1]: percent_embedings[i] })


        return final_result, skills_parse, final_skills,  cosine_score,  skillsmatch, percentage_score,  percentembedings, keywords

class keywords:
    def input(job_title,jd):

        import requests
        import json
        import os
        import pandas as pd

        def get_keywords(jd):
            url = "https://jobfit.perspectico.com/parser"

            input_dict = {"description": {"0": jd}, "skills": {"0": ""}}
            j = json.dumps(input_dict)
            data = {"inputFile": j}

            try:
                response = requests.post(url, data)
                result = response.json()
                # print(result)
                if result['Success']:
                    return result['Keywords']
                else:
                    print("ERROR: Keywords not fetched")
                    result = []
                    return result
            except:
                print("ERROR")
                result = []
                return result

        # 3]:

        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import TextConverter
        from pdfminer.layout import LAParams
        from pdfminer.pdfpage import PDFPage
        import requests
        from io import StringIO
        def convertPDFToText(remote_file):
            ext = remote_file.split('.')[-1]
            if ext == 'pdf':
                print('Extracting data from: {}'.format(remote_file))
                url = remote_file
                r = requests.get(url, allow_redirects=True)
                path = remote_file.split('/')[-1]
                n = path
                open(path, 'wb').write(r.content)
                rsrcmgr = PDFResourceManager()
                retstr = StringIO()
                codec = 'utf-8'
                laparams = LAParams()
                device = TextConverter(rsrcmgr, retstr, laparams=laparams)
                fp = open(path, 'rb')
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                password = ""
                maxpages = 0
                caching = True
                pagenos = set()
                for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                              check_extractable=True):
                    interpreter.process_page(page)
                fp.close()
                device.close()
                string = retstr.getvalue()
                retstr.close()
                os.remove(n)
                return string
            elif ext == 'docx':
                print('Extracting data from: {}'.format(remote_file))
                url = remote_file
                r = requests.get(url, allow_redirects=True)
                path = remote_file.split('/')[-1]
                n = path
                open(path, 'wb').write(r.content)
                from docx import Document
                document = Document(path)
                os.remove(n)
                return '\n'.join([para.text for para in document.paragraphs])


        skills = {}
        percent = {}
        skills_match = {}
        percent_embedings = {}


        # 5]:
        #print(skills)
        def get_closest(word):

            word = word.lower()
            words = [word]
            similar_vals = [1]
            try:
                similar_list = word_vect.most_similar(word)

                for tupl in similar_list:
                    words.append(tupl[0])
                    similar_vals.append(tupl[1])
            except:

                pass

            return words, similar_vals

        # 6]:

        def get_skills(role):
            url = "https://jobfit.perspectico.com/recommendation"

            data = {"jobRole": role}
            try:
                response = requests.post(url, data)
                result = response.json()
                return result
            except:
                pass
        ext = jd.split('.')[-1]
        if ext == 'pdf':
            print('jd in pdf format')
            jd= convertPDFToText(jd)
            print(jd)
        if len(jd) > 0:
            # print('Enter JD')
            s = get_keywords(jd)
            print("jD detected")
        #print(s)
        # print('Enter Job Role')
        job_role = job_title

        d = get_skills(job_role)
        job_role_skills = d['results']['keywords']
        keywords = job_role_skills


        print("final list of skills from api and JD")
        print("=========================")
        print(job_role_skills)
        print(" \n  =========================")
        jd_skills=s




        return job_role_skills,jd_skills







from flask import Flask, render_template, request
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

import requests
import json

from flask import Flask, render_template, request
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
# from voice_analysis import voice_analysis
import requests
import json

app = Flask(__name__)


@app.route('/keywords', methods=['POST', 'GET'])
def result_keywords():
    if request.method == 'POST':
        # result = request.get_json()
        k = request.get_json(force=True)
        #combined words of api and jd
        job_role_skills,jd_skills= keywords.input(k['Job Role'], k['JD'])

    dict={'recommended skills':job_role_skills,'jd skill':jd_skills}

    output = json.dumps(dict)
    return output


@app.route('/resume',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      #result = request.get_json()
      k=request.get_json(force=True)
      print(k)
      #jb_tile=k['job title'].split(',')
      job_role_skills, jd_skills = keywords.input(k['Job Role'], k['JD'])# from user
      job_role_skills=job_role_skills+jd_skills
      result,final_skills,skills_parse,cosine_score,skillsmatch,percentage_score,percent_embedings,keywords_=resume_matcher.input(job_role_skills,word_vect,nlp)
      global skills
      global title
      final_skills=final_skills
      skills_parse = skills_parse
      cosine_score = cosine_score
      skillsmatch = skillsmatch
      percentage_score = percentage_score
      percent_embedings = percent_embedings

      final_dict={"final_skills":final_skills,"skills_parse":skills_parse,
                  "cosine_score": cosine_score,"skillsmatch" : skillsmatch,
                    "percentage_score" : percentage_score,
                    "percent_embedings" : percent_embedings}

      output = json.dumps(final_dict)
      return output







#if __name__ == '__main__':
if __name__ == '__main__':
    from gensim.models.keyedvectors import KeyedVectors
    word_vect = KeyedVectors.load_word2vec_format("./SO_vectors_200.bin", binary=True)
    from spacy.matcher import Matcher
    import spacy

    nlp = spacy.load('en_core_web_sm')
    print("model imported")
    app.run(host='0.0.0.0',debug=True)

