Title: Datacraft with H.P. Lovecraft
Date: 2014-10-20 8:20
Tags: d3, python, sklearn
Category: notebooks
Slug: lovecraft
Author: Ryan Wheeler
Summary: Hacking on Lovecraftian Data


## Data Craft With HP. Lovecraft ##

I have read almost every Lovecraft short story. Some are terrible. So bad.
Trite, silly, racist, just bad. But a few -- Lovecraft nails it. Cosmic chaos, a
sprawling mythos, and a psudo intellectualism abound. And when im not crunching
data with hadoop at work, I try to find datasets I think are neat in my own
time. Also I have really wanted an excuse to use Jake Vanderplas mpld3 library
(matplotlib + d3)

So -- with the help of NLTK and Sklearn,


    from bs4 import BeautifulSoup
    import re
    import urllib2
    import pandas as pd 
    import nltk 
    import itertools
    import pickle
    import numpy as np
    import mpld3
    from collections import defaultdict
    from matplotlib import pyplot as plt
    
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 10)
    %pylab inline
    %matplotlib inline  

    Populating the interactive namespace from numpy and matplotlib


    WARNING: pylab import has clobbered these variables: ['stem']
    `%matplotlib` prevents importing * from pylab and numpy


##Wrangle some Data ##

First we need to grab the corpus we are going to use. Here I found a website
that hosted all of Lovecrafts work, and using Beautiful soup, we can quickly
grab what we need. Python makes this stuff cake.

- We point BS at the parent directory, and first crawl for all links (href),
each like should take us to the actual story.
- Then we create some helper functins that will actually process all the text on
each link
- The final strcuture should be a Pandas DataFrame with all of our data in a
sane format.



    ROOT = 'http://www.psy-q.ch/lovecraft/html/'
    data = urllib2.urlopen(ROOT)


    doc = BeautifulSoup(data)


    links = [ROOT+link.get('href') for link in doc.find_all('a') if 'txt'in link.get('href') ]
    links[:5]




    ['http://www.psy-q.ch/lovecraft/html/alchemis.txt',
     'http://www.psy-q.ch/lovecraft/html/mountains.txt',
     'http://www.psy-q.ch/lovecraft/html/azathoth.txt',
     'http://www.psy-q.ch/lovecraft/html/cave.txt',
     'http://www.psy-q.ch/lovecraft/html/sleep.txt']



At this point we have all the links we need to visit the pages containing all of
Lovecrafts work. We need a couple helper functions to munge this data into the
shape we need. We are aiming to have a DataFrame with where the columns are the
Title, Text, and Publication Date


    def get_titles(page): 
        dirty_titles = page.find_all('li')
        
        clean_titles = []
        for title in dirty_titles: 
            title = str(title)
            title = title.split('[')[0] 
            title = title.replace('<li>','')
            title = title.strip()
            clean_titles.append(title)
        return clean_titles


    def get_text(link):  
        doc = urllib2.urlopen(link).read()
        return doc
            


    def get_date(text): 
        date_text = re.findall(r'Written\s.*',text)
        if date_text:     
            date = re.findall(r'\d+',date_text[0])
            if date:
                year = max(map(int,date))
                return year

Now that we have our links and our helper functions, we can create the data
structure.
First we create the titles from parsing the index page. Then we lazily iterate
the link list and the title list at the same time using izip. The default dict
will get our data in the correct structure for the the Pandas DataFrame
constructor


    titles = get_titles(doc)
    titles[:5]




    ['The Alchemist',
     'At the Mountains of Madness',
     'Azathoth',
     'The Beast in the Cave',
     'Beyond the Wall of Sleep']




    lovecraft = defaultdict(list)
    
    for (title,link) in itertools.izip(titles,links): 
        text = get_text(link)
        date = get_date(text)
        lovecraft['date'].append(date)
        lovecraft['title'].append(title)
        lovecraft['text'].append(text)

Once we have the articles in a dictionary we can pickle the object for later


    import pickle
    pickle.dump(lovecraft,open( "lovecraft.p", "wb" ))

And we can then read in the serialized object

## Frequency of Other Gods, Great Old Ones etc ##

Load up our new corpus


    lovecraft = pickle.load(open( "lovecraft.p", "rb" ))

So I kind of wanted to find the frequency of every Diety mentiond in the
Lovecraft corpus and wrote this function to parse through a wikipedia table, but
ended up not using. Leaving in for postertiy.

We need to get a list of all the dieties in Lovecrafts mythos -- a quick search
shows an html table on wikipedia


    def get_wiki_table(_url= 'http://en.wikipedia.org/wiki/Cthulhu_Mythos_deities', 
                       cnames = ['name','epithet','description','references']): 
        data = urllib2.urlopen(_url)
        doc = BeautifulSoup(data)
        table = doc.find("table", { "class" : "wikitable"})
        
        dd = defaultdict(list)
        
        for row in table.findAll("tr"): 
            cells = row.findAll("td") 
            if len(cells) == len(cnames): 
                dd[cnames[0]].append(cells[0].find(text=True))
                dd[cnames[1]].append(cells[1].find(text=True))
                dd[cnames[2]].append(cells[2].find(text=True))
                dd[cnames[3]].append(cells[3].find(text=True))
        return pd.DataFrame(dd,columns = cnames)


    #old_ones = get_wiki_table()

At this point we have our corpra, we and we have the data in the first form we
need. Now we can do some pandas wrangling. The handy defaultdict we created can
be passed to the DataFrame constructor.


    df = pd.DataFrame(lovecraft).sort('date') 

Here we can see the basic stucture we aimed for.


    df.head(10)




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>text</th>
      <th>title</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>146</th>
      <td> 1897</td>
      <td> The Little Glass Bottle\n\n  by H. P. Lovecraf...</td>
      <td> Supernatural Horror in Literature with bibliog...</td>
    </tr>
    <tr>
      <th>149</th>
      <td> 1898</td>
      <td> The Secret Cave\nor John Lees adventure\n\n  b...</td>
      <td>                     The Mystery of the Grave-Yard</td>
    </tr>
    <tr>
      <th>148</th>
      <td> 1898</td>
      <td> The Mystery Of The Grave-Yard\nor "A Dead Man'...</td>
      <td>                               The Mysterious Ship</td>
    </tr>
    <tr>
      <th>147</th>
      <td> 1902</td>
      <td> The Mysteriovs Ship\n\n  by H. P. Lovecraft\n\...</td>
      <td>                           The Little Glass Bottle</td>
    </tr>
    <tr>
      <th>3  </th>
      <td> 1905</td>
      <td> The Beast in the Cave\n\n  by H. P. Lovecraft\...</td>
      <td>                             The Beast in the Cave</td>
    </tr>
    <tr>
      <th>0  </th>
      <td> 1908</td>
      <td> The Alchemist\n\n  by H. P. Lovecraft\n\n     ...</td>
      <td>                                     The Alchemist</td>
    </tr>
    <tr>
      <th>58 </th>
      <td> 1917</td>
      <td> The Tomb\n\n  by H. P. Lovecraft\n\n          ...</td>
      <td>                                          The Tomb</td>
    </tr>
    <tr>
      <th>12 </th>
      <td> 1917</td>
      <td> Dagon\n\n  by H. P. Lovecraft\n\n             ...</td>
      <td>                                             Dagon</td>
    </tr>
    <tr>
      <th>46 </th>
      <td> 1917</td>
      <td> A Reminiscence Of Dr. Samuel Johnson\n\n  by H...</td>
      <td>              A Reminiscence Of Dr. Samuel Johnson</td>
    </tr>
    <tr>
      <th>77 </th>
      <td> 1918</td>
      <td> The Green Meadow\n\n  by H. P. Lovecraft and W...</td>
      <td>         The Green Meadow with Winifred V. Jackson</td>
    </tr>
  </tbody>
</table>
</div>



An idea I had was to count each time the word 'cthulhu' occurs in each work.
Being Lovecrafts most famous and the eponymous Cthulhu mythos.


This function declares declares another function inside that tokenizes sentences
then tokenizes words and returns a flattend generator that can be consumed by
collections.Counter. We can then access the counter dictionary based on our
input word and retrieve the number of occurences, per document, of the word.
Deffinatly overkill, but thats half the fun.


    import collections 
    def get_wordcount(text,word): 
        
        def l_tokenizer(text): 
            text = text.lower()
            text.replace('\n','')
            sent_tokens = nltk.sent_tokenize(text)
            word_tokens = [nltk.word_tokenize(sent) for sent in sent_tokens]
            return itertools.chain.from_iterable(word_tokens)
        
        
        word_count = collections.Counter(l_tokenizer(text))
        return word_count[word]
        
        

We can use the above function in the following manner



    df["cthulhu"] = df.text.apply(lambda x: get_wordcount(x, 'cthulhu'))
    df["yog-sothoth"] = df.text.apply(lambda x: get_wordcount(x, 'yog-sothoth'))
    df.sort("cthulhu", axis=0,ascending=False).head(10)





<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>text</th>
      <th>title</th>
      <th>cthulhu</th>
      <th>yog-sothoth</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>6  </th>
      <td> 1926</td>
      <td> The Call of Cthulhu\n\n  by H. P. Lovecraft\n\...</td>
      <td>                               The Call of Cthulhu</td>
      <td> 24</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>1  </th>
      <td> 1931</td>
      <td> At the Mountains of Madness\n\n  by H. P. Love...</td>
      <td>                       At the Mountains of Madness</td>
      <td>  6</td>
      <td> 1</td>
    </tr>
    <tr>
      <th>64 </th>
      <td> 1930</td>
      <td> The Whisperer in Darkness\n\n  by H. P. Lovecr...</td>
      <td>                         The Whisperer in Darkness</td>
      <td>  5</td>
      <td> 1</td>
    </tr>
    <tr>
      <th>48 </th>
      <td> 1931</td>
      <td> The Shadow Over Innsmouth\n\n  by H. P. Lovecr...</td>
      <td>                         The Shadow Over Innsmouth</td>
      <td>  3</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>75 </th>
      <td>  NaN</td>
      <td> The Electic Executioner\n\n  by H. P. Lovecraf...</td>
      <td>   The Electric Executioner with Adolphe de Castro</td>
      <td>  3</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>80 </th>
      <td> 1932</td>
      <td> The Horror in the Museum\n\n  by H. P. Lovecra...</td>
      <td>         The Horror in the Museum with Hazel Heald</td>
      <td>  2</td>
      <td> 1</td>
    </tr>
    <tr>
      <th>142</th>
      <td> 1927</td>
      <td> History of the Necronomicon\n\n  by H.P. Lovec...</td>
      <td>                             The Despised Pastoral</td>
      <td>  2</td>
      <td> 2</td>
    </tr>
    <tr>
      <th>90 </th>
      <td> 1933</td>
      <td> Through the Gates of the Silver Key\n\n  by H....</td>
      <td> Through the Gates of the Silver Key with E. Ho...</td>
      <td>  1</td>
      <td> 1</td>
    </tr>
    <tr>
      <th>120</th>
      <td>  NaN</td>
      <td> The Messenger\n\n  by H.P. Lovecraft\n\n      ...</td>
      <td>                                     The Messenger</td>
      <td>  1</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>85 </th>
      <td> 1930</td>
      <td> The Mound\n\n  by H. P. Lovecraft and Zealia B...</td>
      <td>                      The Mound with Zealia Bishop</td>
      <td>  1</td>
      <td> 0</td>
    </tr>
  </tbody>
</table>
</div>




    from collections import defaultdict
    
    diety_occurences = dict()
    dieties = df.columns[~df.columns.isin(['date','text','title'])]
    
    for diety in dieties: 
        #sig_rows = df_cth = df[['date','cthulhu','title']][df[diety] > 0]
        sig_rows = df[['date','title',diety]][df[diety] > 0]
        agg = sig_rows.groupby('date').sum() 
        count = agg.values 
        years = map(int,agg.index)
        tupe = tuple([count,years])
        diety_occurences[diety] = tupe


    diety_occurences['cthulhu'][0]




    array([[24],
           [ 2],
           [ 1],
           [ 7],
           [ 9],
           [ 2],
           [ 1]])



We could go crazy here and use the get_wiki_table() function and loop through
all possible dieties and create like, 100 bubble charts. Not going to do the but
here are two - Mouse over the bubbles to get tooltips --


    import random
    #numpy.random.seed(42)
    
    
    fig, ax = plt.subplots(2,subplot_kw=dict(axisbg='#EEEEEE',), figsize =(11,11))
    for i, diety in enumerate(diety_occurences.keys()):
        count , years = diety_occurences[diety]
        N = len(count)
        ax[i].autoscale(False)
        ax[i].set_ylim([-4,12])
        ax[i].set_xlim([-5,10])
        r_x = [0,3.77,3.21,3,4,5.7,6.34]
        r_y = [6,4.1,8.5,6.7,1,6.9,2.3] 
    
        scatter = ax[i].scatter(r_x,
                        r_y,
                        c= "aquamarine",
                        alpha=0.4,
                        cmap=cm.Blues,
                        s =  1000 * count)
    
    
        ax[i].grid(color='white', linestyle='solid')
        labels = ['Word Occurences: {0} | Year: {1}'.format(c,y) for (c,y) in zip(count,years)]
    #--- Used to have mouse over coordinates, can modify position by adjusting coordinates in r_x, r_y-----         
    #labels = ['{0},{1}'.format(x,y) for (x,y) in zip(r_x,r_y)] 
    
        ax[i].set_title("Number of times {0} was mentioned in a given year".format(diety))
        tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
        mpld3.plugins.connect(fig, tooltip)
    
    mpld3.display()







<style>

</style>

<div id="fig_el27871404686932666402826352967"></div>
<script>
function mpld3_load_lib(url, callback){
  var s = document.createElement('script');
  s.src = url;
  s.async = true;
  s.onreadystatechange = s.onload = callback;
  s.onerror = function(){console.warn("failed to load library " + url);};
  document.getElementsByTagName("head")[0].appendChild(s);
}

if(typeof(mpld3) !== "undefined" && mpld3._mpld3IsLoaded){
   // already loaded: just create the figure
   !function(mpld3){
       
       mpld3.draw_figure("fig_el27871404686932666402826352967", {"axes": [{"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of times yog-sothoth was mentioned in a given year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0179211469534051], "rotation": -0.0, "id": "el2787140468693590480"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468693270096", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468692774288", "pathtransforms": [[121.71612389003693, 0.0, 0.0, 121.71612389003693, 0.0, 0.0], [126.68615834434867, 0.0, 0.0, 126.68615834434867, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#7FFFD4"]}], "xscale": "linear", "bbox": [0.125, 0.54772727272727284, 0.77500000000000002, 0.35227272727272718]}, {"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of times cthulhu was mentioned in a given year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0179211469534051], "rotation": -0.0, "id": "el2787140468693747216"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468694212368", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468692830352", "pathtransforms": [[172.13259316477408, 0.0, 0.0, 172.13259316477408, 0.0, 0.0], [49.69039949999532, 0.0, 0.0, 49.69039949999532, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [105.40925533894597, 0.0, 0.0, 105.40925533894597, 0.0, 0.0], [49.69039949999532, 0.0, 0.0, 49.69039949999532, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#7FFFD4"]}], "xscale": "linear", "bbox": [0.125, 0.12500000000000011, 0.77500000000000002, 0.35227272727272724]}], "height": 880.0, "width": 880.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Word Occurences: [12] | Year: 1927", "Word Occurences: [13] | Year: 1928", "Word Occurences: [1] | Year: 1930", "Word Occurences: [1] | Year: 1931", "Word Occurences: [1] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692774288"}, {"voffset": 10, "labels": ["Word Occurences: [24] | Year: 1926", "Word Occurences: [2] | Year: 1927", "Word Occurences: [1] | Year: 1928", "Word Occurences: [7] | Year: 1930", "Word Occurences: [9] | Year: 1931", "Word Occurences: [2] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692830352"}], "data": {"data01": [[0.0, 6.0], [3.77, 4.1], [3.21, 8.5], [3.0, 6.7], [4.0, 1.0], [5.7, 6.9], [6.34, 2.3]]}, "id": "el2787140468693266640"});
   }(mpld3);
}else if(typeof define === "function" && define.amd){
   // require.js is available: use it to load d3/mpld3
   require.config({paths: {d3: "https://mpld3.github.io/js/d3.v3.min"}});
   require(["d3"], function(d3){
      window.d3 = d3;
      mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
         
         mpld3.draw_figure("fig_el27871404686932666402826352967", {"axes": [{"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of times yog-sothoth was mentioned in a given year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0179211469534051], "rotation": -0.0, "id": "el2787140468693590480"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468693270096", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468692774288", "pathtransforms": [[121.71612389003693, 0.0, 0.0, 121.71612389003693, 0.0, 0.0], [126.68615834434867, 0.0, 0.0, 126.68615834434867, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#7FFFD4"]}], "xscale": "linear", "bbox": [0.125, 0.54772727272727284, 0.77500000000000002, 0.35227272727272718]}, {"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of times cthulhu was mentioned in a given year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0179211469534051], "rotation": -0.0, "id": "el2787140468693747216"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468694212368", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468692830352", "pathtransforms": [[172.13259316477408, 0.0, 0.0, 172.13259316477408, 0.0, 0.0], [49.69039949999532, 0.0, 0.0, 49.69039949999532, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [105.40925533894597, 0.0, 0.0, 105.40925533894597, 0.0, 0.0], [49.69039949999532, 0.0, 0.0, 49.69039949999532, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#7FFFD4"]}], "xscale": "linear", "bbox": [0.125, 0.12500000000000011, 0.77500000000000002, 0.35227272727272724]}], "height": 880.0, "width": 880.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Word Occurences: [12] | Year: 1927", "Word Occurences: [13] | Year: 1928", "Word Occurences: [1] | Year: 1930", "Word Occurences: [1] | Year: 1931", "Word Occurences: [1] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692774288"}, {"voffset": 10, "labels": ["Word Occurences: [24] | Year: 1926", "Word Occurences: [2] | Year: 1927", "Word Occurences: [1] | Year: 1928", "Word Occurences: [7] | Year: 1930", "Word Occurences: [9] | Year: 1931", "Word Occurences: [2] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692830352"}], "data": {"data01": [[0.0, 6.0], [3.77, 4.1], [3.21, 8.5], [3.0, 6.7], [4.0, 1.0], [5.7, 6.9], [6.34, 2.3]]}, "id": "el2787140468693266640"});
      });
    });
}else{
    // require.js not available: dynamically load d3 & mpld3
    mpld3_load_lib("https://mpld3.github.io/js/d3.v3.min.js", function(){
         mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
                 
                 mpld3.draw_figure("fig_el27871404686932666402826352967", {"axes": [{"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of times yog-sothoth was mentioned in a given year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0179211469534051], "rotation": -0.0, "id": "el2787140468693590480"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468693270096", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468692774288", "pathtransforms": [[121.71612389003693, 0.0, 0.0, 121.71612389003693, 0.0, 0.0], [126.68615834434867, 0.0, 0.0, 126.68615834434867, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#7FFFD4"]}], "xscale": "linear", "bbox": [0.125, 0.54772727272727284, 0.77500000000000002, 0.35227272727272718]}, {"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of times cthulhu was mentioned in a given year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0179211469534051], "rotation": -0.0, "id": "el2787140468693747216"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468694212368", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468692830352", "pathtransforms": [[172.13259316477408, 0.0, 0.0, 172.13259316477408, 0.0, 0.0], [49.69039949999532, 0.0, 0.0, 49.69039949999532, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [105.40925533894597, 0.0, 0.0, 105.40925533894597, 0.0, 0.0], [49.69039949999532, 0.0, 0.0, 49.69039949999532, 0.0, 0.0], [35.136418446315325, 0.0, 0.0, 35.136418446315325, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#7FFFD4"]}], "xscale": "linear", "bbox": [0.125, 0.12500000000000011, 0.77500000000000002, 0.35227272727272724]}], "height": 880.0, "width": 880.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Word Occurences: [12] | Year: 1927", "Word Occurences: [13] | Year: 1928", "Word Occurences: [1] | Year: 1930", "Word Occurences: [1] | Year: 1931", "Word Occurences: [1] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692774288"}, {"voffset": 10, "labels": ["Word Occurences: [24] | Year: 1926", "Word Occurences: [2] | Year: 1927", "Word Occurences: [1] | Year: 1928", "Word Occurences: [7] | Year: 1930", "Word Occurences: [9] | Year: 1931", "Word Occurences: [2] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692830352"}], "data": {"data01": [[0.0, 6.0], [3.77, 4.1], [3.21, 8.5], [3.0, 6.7], [4.0, 1.0], [5.7, 6.9], [6.34, 2.3]]}, "id": "el2787140468693266640"});
            })
         });
}
</script>



We can clean the plot up a little and make it bigger


    import random
    numpy.random.seed(42)
    
    
    
    
    fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize =(12,12))
    # Tick lines can be removed via: 
    #fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE',xticks=[], yticks =[]), figsize =(12,12))
    count , years = diety_occurences['cthulhu']
    N = len(count)
    ax.autoscale(False)
    ax.set_ylim([-4,12])
    ax.set_xlim([-5,10])
    
    r_x = [0,3.77,3.21,5,4,5.7,6.34]
    r_y = [6,4.1,8.5,6.7,1,3.9,2.3] 
    
    scatter = ax.scatter(r_x,
                        r_y,
                        c=np.random.random(size=N),
                        alpha=0.4,
                        cmap=cm.cool,
                        s =  3500 * count)
    
    ax.grid(color='white', linestyle='solid')
    labels = ["Word Occurences: {0} | Year: {1}".format(c,y) for (c,y) in zip(count,years)]
    #--- Used to have mouse over coordinates, can modify position by adjusting coordinates in r_x, r_y-----         
    #labels = ['{0},{1}'.format(x,y) for (x,y) in zip(r_x,r_y)] 
    
    ax.set_title("Number of Times C'thulhu was mentioned in a year")
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
    
    mpld3.display()







<style>

</style>

<div id="fig_el27871404686949721769032564529"></div>
<script>
function mpld3_load_lib(url, callback){
  var s = document.createElement('script');
  s.src = url;
  s.async = true;
  s.onreadystatechange = s.onload = callback;
  s.onerror = function(){console.warn("failed to load library " + url);};
  document.getElementsByTagName("head")[0].appendChild(s);
}

if(typeof(mpld3) !== "undefined" && mpld3._mpld3IsLoaded){
   // already loaded: just create the figure
   !function(mpld3){
       
       mpld3.draw_figure("fig_el27871404686949721769032564529", {"axes": [{"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of Times C'thulhu was mentioned in a year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0074671445639187], "rotation": -0.0, "id": "el2787140468693738128"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468698534288", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468695065680", "pathtransforms": [[322.0305943597653, 0.0, 0.0, 322.0305943597653, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [65.73421981221796, 0.0, 0.0, 65.73421981221796, 0.0, 0.0], [173.91639824998364, 0.0, 0.0, 173.91639824998364, 0.0, 0.0], [197.20265943665385, 0.0, 0.0, 197.20265943665385, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [65.73421981221796, 0.0, 0.0, 65.73421981221796, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#59A5FF", "#FF00FF", "#C13EFF", "#9B64FF", "#1CE3FF", "#1CE3FF", "#00FFFF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 960.0, "width": 960.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Word Occurences: [24] | Year: 1926", "Word Occurences: [2] | Year: 1927", "Word Occurences: [1] | Year: 1928", "Word Occurences: [7] | Year: 1930", "Word Occurences: [9] | Year: 1931", "Word Occurences: [2] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468695065680"}], "data": {"data01": [[0.0, 6.0], [3.77, 4.1], [3.21, 8.5], [5.0, 6.7], [4.0, 1.0], [5.7, 3.9], [6.34, 2.3]]}, "id": "el2787140468694972176"});
   }(mpld3);
}else if(typeof define === "function" && define.amd){
   // require.js is available: use it to load d3/mpld3
   require.config({paths: {d3: "https://mpld3.github.io/js/d3.v3.min"}});
   require(["d3"], function(d3){
      window.d3 = d3;
      mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
         
         mpld3.draw_figure("fig_el27871404686949721769032564529", {"axes": [{"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of Times C'thulhu was mentioned in a year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0074671445639187], "rotation": -0.0, "id": "el2787140468693738128"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468698534288", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468695065680", "pathtransforms": [[322.0305943597653, 0.0, 0.0, 322.0305943597653, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [65.73421981221796, 0.0, 0.0, 65.73421981221796, 0.0, 0.0], [173.91639824998364, 0.0, 0.0, 173.91639824998364, 0.0, 0.0], [197.20265943665385, 0.0, 0.0, 197.20265943665385, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [65.73421981221796, 0.0, 0.0, 65.73421981221796, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#59A5FF", "#FF00FF", "#C13EFF", "#9B64FF", "#1CE3FF", "#1CE3FF", "#00FFFF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 960.0, "width": 960.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Word Occurences: [24] | Year: 1926", "Word Occurences: [2] | Year: 1927", "Word Occurences: [1] | Year: 1928", "Word Occurences: [7] | Year: 1930", "Word Occurences: [9] | Year: 1931", "Word Occurences: [2] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468695065680"}], "data": {"data01": [[0.0, 6.0], [3.77, 4.1], [3.21, 8.5], [5.0, 6.7], [4.0, 1.0], [5.7, 3.9], [6.34, 2.3]]}, "id": "el2787140468694972176"});
      });
    });
}else{
    // require.js not available: dynamically load d3 & mpld3
    mpld3_load_lib("https://mpld3.github.io/js/d3.v3.min.js", function(){
         mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
                 
                 mpld3.draw_figure("fig_el27871404686949721769032564529", {"axes": [{"xlim": [-5.0, 10.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "Number of Times C'thulhu was mentioned in a year", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 12.0, "position": [0.5, 1.0074671445639187], "rotation": -0.0, "id": "el2787140468693738128"}], "zoomable": true, "images": [], "xdomain": [-5.0, 10.0], "ylim": [-4.0, 12.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468698534288", "ydomain": [-4.0, 12.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el2787140468695065680", "pathtransforms": [[322.0305943597653, 0.0, 0.0, 322.0305943597653, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [65.73421981221796, 0.0, 0.0, 65.73421981221796, 0.0, 0.0], [173.91639824998364, 0.0, 0.0, 173.91639824998364, 0.0, 0.0], [197.20265943665385, 0.0, 0.0, 197.20265943665385, 0.0, 0.0], [92.96222517045284, 0.0, 0.0, 92.96222517045284, 0.0, 0.0], [65.73421981221796, 0.0, 0.0, 65.73421981221796, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.4], "facecolors": ["#59A5FF", "#FF00FF", "#C13EFF", "#9B64FF", "#1CE3FF", "#1CE3FF", "#00FFFF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 960.0, "width": 960.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Word Occurences: [24] | Year: 1926", "Word Occurences: [2] | Year: 1927", "Word Occurences: [1] | Year: 1928", "Word Occurences: [7] | Year: 1930", "Word Occurences: [9] | Year: 1931", "Word Occurences: [2] | Year: 1932", "Word Occurences: [1] | Year: 1933"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468695065680"}], "data": {"data01": [[0.0, 6.0], [3.77, 4.1], [3.21, 8.5], [5.0, 6.7], [4.0, 1.0], [5.7, 3.9], [6.34, 2.3]]}, "id": "el2787140468694972176"});
            })
         });
}
</script>



##TF-IDF##

So counting things and bubble charts are fun -- so is Scikit Learn. We are going
to create a document term matrix using the TF-IDF vectorizor. TF-IDF is an older
information retrieval algorithm that attempts to quantify 'important' words.
Words are import in they appear a large number of times in a single story, and
few times in the entire collection of stories.

But first we need to do some preprocessing on the text.

NLTK provides some great ways of doing this. We are going to:
- lower case the text
- Regex only words
- tokenize words / sents
- remove stop words (a, the, etc)
- stem the words (this makes 'bird' and 'birds' the same word, we do not want
slight variations of a word to be counted as a  completely new word

We need to create a tokenizing function that will tokenize a test we pass in. We
can build this using some standard functions from NLTK. We then need to get the
dataframe into a dictionary,where the key is the doc title, and the value is the
doct text.


    from nltk import stem
    from nltk.tokenize import RegexpTokenizer
    from nltk.corpus import stopwords
    
    porter = stem.porter.PorterStemmer()
    
    def preprocess(text):
        sentence = text.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        stemmed = [porter.stem(word) for word in filtered_words]
        return " ".join(stemmed)


    preprocess('The bird birds. The swimming boy took a swim') 




    'bird bird swim boy took swim'



Instantiate the sklearn vectorizer and pass in some params
- ngram_range will create a document term matrix with every column a single gram
(word), we could do bigram with (1,2) bigrams are pairs of words that co occur.
- norm will do l2 regularization


    from sklearn.feature_extraction.text import TfidfVectorizer
    
    vectorizer = TfidfVectorizer(preprocessor=preprocess,ngram_range=(1,1), norm='l2', smooth_idf = True, use_idf=True)


    X = vectorizer.fit_transform(df.text)
    idx = df.title.values # index is the doc titles 
    cols = [feature for feature in vectorizer.get_feature_names()]
    dtm = pd.DataFrame(X.todense(),columns=cols, index=idx)
    dtm.head()




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>00</th>
      <th>000</th>
      <th>01</th>
      <th>05</th>
      <th>0500</th>
      <th>07</th>
      <th>08</th>
      <th>0ther</th>
      <th>10</th>
      <th>100</th>
      <th>...</th>
      <th>zone</th>
      <th>zoo</th>
      <th>zoog</th>
      <th>zoolog</th>
      <th>zothiqu</th>
      <th>zulu</th>
      <th>zuni</th>
      <th>zur</th>
      <th>zura</th>
      <th>zuro</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Supernatural Horror in Literature with bibliography</th>
      <td> 0.179763</td>
      <td> 0.000000</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0.000000</td>
      <td> 0</td>
      <td>...</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>The Mystery of the Grave-Yard</th>
      <td> 0.000000</td>
      <td> 0.057790</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0.087192</td>
      <td> 0</td>
      <td>...</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>The Mysterious Ship</th>
      <td> 0.000000</td>
      <td> 0.021958</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0.082825</td>
      <td> 0</td>
      <td>...</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>The Little Glass Bottle</th>
      <td> 0.000000</td>
      <td> 0.045416</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0.000000</td>
      <td> 0</td>
      <td>...</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
    </tr>
    <tr>
      <th>The Beast in the Cave</th>
      <td> 0.000000</td>
      <td> 0.000000</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0.000000</td>
      <td> 0</td>
      <td>...</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
      <td> 0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 18615 columns</p>
</div>



Now that we have highly dimensional data we can reduce the dimensions, then
visualize. While Cthulhu may exist in multidimensions, human brains are not
great above.

<img src="http://upload.wikimedia.org/wikipedia/commons/5/55/Tesseract.gif">


####Visualization of High Demension Data####
PCA for dimensional reduction


    from sklearn.decomposition import PCA 
    
    pca = PCA(n_components=2)
    tf_pca = pca.fit_transform(X.todense())
    print "Explained Variance", pca.explained_variance_ratio_.sum() * 100

    Explained Variance 7.27156563985


2 comps is not enough to explain variance -- but it is enough for a blog post


    %matplotlib inline
        
    fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize =(10,10))
    lables = df.title.values
    N = len(lables)
    p_x = tf_pca[:,0]
    p_y = tf_pca[:,1]
    
    scatter = ax.scatter(p_x,
                         p_y,
                         c=np.random.random(size=N),
                         alpha=0.3,
                         cmap=cm.cool,
                         s = 400 )
    ax.grid(color='white', linestyle='solid')
    ax.set_title("2 Princomps of Lovecraft TF-IDF Data", size=25)
    labels = ['{0}'.format(title) for title in lables]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
    #plt.axvspan(-.83,-.79, color='turquoise', alpha=0.5)             will add a vertical bar highlight 
    mpld3.display()






<style>

</style>

<div id="fig_el30111401337129737764893789309"></div>
<script>
function mpld3_load_lib(url, callback){
  var s = document.createElement('script');
  s.src = url;
  s.async = true;
  s.onreadystatechange = s.onload = callback;
  s.onerror = function(){console.warn("failed to load library " + url);};
  document.getElementsByTagName("head")[0].appendChild(s);
}

if(typeof(mpld3) !== "undefined" && mpld3._mpld3IsLoaded){
   // already loaded: just create the figure
   !function(mpld3){
       
       mpld3.draw_figure("fig_el30111401337129737764893789309", {"axes": [{"xlim": [-0.80000000000000004, 0.60000000000000009], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "2 Princomps of Lovecraft TF-IDF Data", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 25.0, "position": [0.5, 1.0089605734767024], "rotation": -0.0, "id": "el3011140133712764880"}], "zoomable": true, "images": [], "xdomain": [-0.80000000000000004, 0.60000000000000009], "ylim": [-0.40000000000000002, 1.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el3011140133715543312", "ydomain": [-0.40000000000000002, 1.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el3011140133712439632", "pathtransforms": [[22.22222222222222, 0.0, 0.0, 22.22222222222222, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.3], "facecolors": ["#5CA3FF", "#2BD3FF", "#03FCFF", "#43BCFF", "#8579FF", "#E31BFF", "#E916FF", "#6798FF", "#A05FFF", "#CF30FF", "#1FE0FF", "#6D92FF", "#619EFF", "#BD41FF", "#718DFF", "#7E81FF", "#04FBFF", "#7B83FF", "#44BBFF", "#B748FF", "#CC32FF", "#BB44FF", "#24DBFF", "#49B5FF", "#926DFF", "#BC42FF", "#47B8FF", "#51ADFF", "#59A6FF", "#926DFF", "#BF40FF", "#43BCFF", "#639CFF", "#718EFF", "#59A6FF", "#CF30FF", "#DF20FF", "#8B74FF", "#CC32FF", "#34CBFF", "#20DFFF", "#639CFF", "#3FC0FF", "#DD21FF", "#D926FF", "#5FA0FF", "#38C6FF", "#38C7FF", "#DB24FF", "#59A6FF", "#F30BFF", "#6B93FF", "#04FBFF", "#E618FF", "#619DFF", "#45BAFF", "#2FD0FF", "#F20DFF", "#24DBFF", "#A05FFF", "#BE41FF", "#CB34FF", "#FE00FF", "#26D9FF", "#FB04FF", "#05FAFF", "#2CD3FF", "#748BFF", "#C738FF", "#D12EFF", "#FF00FF", "#01FEFF", "#1AE5FF", "#EA15FF", "#CC32FF", "#F20DFF", "#639CFF", "#BC42FF", "#1DE2FF", "#BD41FF", "#3AC5FF", "#758AFF", "#1DE2FF", "#6D92FF", "#6E91FF", "#C33BFF", "#8F70FF", "#26D9FF", "#7E81FF", "#8C72FF", "#916EFF", "#04FBFF", "#8A75FF", "#F906FF", "#1AE5FF", "#47B8FF", "#DF20FF", "#5FA0FF", "#718EFF", "#0AF5FF", "#E817FF", "#837BFF", "#738CFF", "#F708FF", "#AF50FF", "#649BFF", "#AD51FF", "#58A7FF", "#24DBFF", "#2ED1FF", "#718EFF", "#DD21FF", "#D02FFF", "#5FA0FF", "#1DE2FF", "#EE10FF", "#D926FF", "#C33CFF", "#46B9FF", "#0FF0FF", "#48B7FF", "#649BFF", "#BD41FF", "#C33CFF", "#1DE2FF", "#E718FF", "#609FFF", "#F608FF", "#758AFF", "#00FFFF", "#8778FF", "#18E7FF", "#7887FF", "#6996FF", "#22DDFF", "#738CFF", "#936BFF", "#FD01FF", "#45BAFF", "#C13EFF", "#A857FF", "#00FFFF", "#758AFF", "#CA35FF", "#EA15FF", "#03FCFF", "#A25DFF", "#ED11FF", "#8F70FF", "#10EFFF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 800.0, "width": 800.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Supernatural Horror in Literature with bibliography", "The Mystery of the Grave-Yard", "The Mysterious Ship", "The Little Glass Bottle", "The Beast in the Cave", "The Alchemist", "The Tomb", "Dagon", "A Reminiscence Of Dr. Samuel Johnson", "The Green Meadow with Winifred V. Jackson", "Polaris", "The Statement of Randolph Carter", "Memory", "Old Bugs", "The Doom That Came to Sarnath", "Beyond the Wall of Sleep", "The Transition of Juan Romero", "The White Ship", "The Picture in the House", "The Tree", "Nyarlathotep", "The Street", "The Temple", "The Terrible Old Man", "The Crawling Chaos with Elizabeth Berkeley", "Poetry and the Gods with Anna Helen Crofts", "From Beyond", "The Cats of Ulthar", "Ex Oblivione", "Facts Concerning the Late Arthur Jermyn and His Family", "Celephais", "The Outsider", "The Moon-Bog", "The Quest of Iranon", "The Music of Erich Zann", "The Nameless City", "The Other Gods", "Waste Paper", "Herbert West: Reanimator", "The Horror at Martin's Beach with Sonia H. Greene", "The Lurking Fear", "Azathoth", "The Hound", "Hypnos", "What the Moon Brings", "The Rats in the Walls", "The Unnamable", "The Festival", "Providence", "Imprisoned with the Pharaos", "The Shunned House", "He", "The Horror at Red Hook", "In The Vault", "<!-- -->At the Root  <!--", "The Call of Cthulhu", "The Strange High House in the Mist", "The Silver Key", "Pickman's Model", "Cool Air", "The Descendant", "The Case of Charles Dexter Ward", "The Despised Pastoral", "The Colour Out of Space", "The Thing in the Moonlight with J. Chapman Miske", "The Dream Quest of Unknown Kadath", "The Last Test with Adolphe de Castro", "The Curse of Yig with Zealia Bishop", "The Dunwich Horror", "Fungi from Yuggoth", "Medusa's Coil with Zealia Bishop", "The Mound with Zealia Bishop", "The Whisperer in Darkness", "The Shadow Over Innsmouth", "At the Mountains of Madness", "The Trap with Henry S. Whitehead", "The Man of Stone with Hazel Heald", "Dreams in the Witch-House", "The Horror in the Museum with Hazel Heald", "The Thing on the Doorstep", "Out of the Aeons with Hazel Heald", "Notes On Writing Weird Fiction", "Through the Gates of the Silver Key with E. Hoffmann Price", "The Winged Death with Hazel Heald", "The Book", "The Tree on the Hill with Duane W. Rimel", "The Challenge from Beyond with C. L. Moore, A. Merritt, Robert E. Howard, and Frank Belknap Long", "The Haunter Of The Dark", "Till A' the Seas with R. H. Barlow", "The Shadow Out of Time", "The Diary of Alonzo Typer with William Lumley", "The Disinterment with Duane W. Rimel", "The Horror in the Burying Ground with Hazel Heald", "The Night Ocean with R. H. Barlow", "Within The Walls Of Eryx with Kenneth Sterling", "The Evil Clergyman", "Ibid", "Sweet Ermengarde by Percy Simple", "The Very Old Folk", "Ashes with C. M. Eddy", "The Battle that Ended the Century with Robert Barlow", "Collapsing Cosmoses with Robert Barlow", "Deaf, Dumb, and Blind with C. M. Eddy", "The Electric Executioner with Adolphe de Castro", "The Ghost Eater with C. M. Eddy", "The Loved Dead with C. M. Eddy", "Two Black Bottles with Wilfred Blanch Talman", "An American to Mother England", "Astrophobos", "The Bride of the Sea", "The Cats", "Christmas Blessings", "Christmas Snows", "Christmastide", "The City", "The Conscript", "Despair", "To Edward John Moreton Drax Plunkett, Eighteenth Baron Dunsany", "Egyptian Christmas", "Fact and Fancy", "Festival", "The Garden", "Good Saint Nick", "Halcyon Days", "Hallowe'en in a Suburb", "The House", "Laeta; A Lament", "Lines on General Robert E. Lee", "Little Tiger", "The Messenger", "Nathanica", "Nemesis", "Ode for July Fourth, 1917", "On Receiving a Picture of Swans", "Pacifist War Song - 1917", "The Peace Advocate", "The Poe-ets Nightmare", "Poemata Minoria, Volume II", "The Rose of England", "On Reading Lord Dunsany's <i>Book of Wonder</i>", "Revelation", "St. John", "Sunset", "Tosh Bosh", "Where Once Poe Walked", "The Wood", "The Allowable Rhyme", "Cats and Dogs", "History of the Necronomicon", "Metrical Regularity"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el3011140133712439632"}], "data": {"data01": [[-0.1450877244248166, -0.012345432476003794], [-0.09581806267291283, -0.011097820110439183], [-0.14086914576745493, -0.023736819875285763], [-0.1901737728365357, -0.050740935125963955], [0.16248363598111987, 0.0469988322055736], [0.13896771892986473, 0.009198886379716909], [0.2052653732540268, 0.02914791590081186], [0.15795325772115862, -0.005467277709723869], [-0.08229437687259504, -0.008823667297106616], [0.15338138265019663, 0.00640114547686118], [-0.0011957655615174052, -0.08859784809117176], [0.08075139196725484, 0.014790235313773416], [-0.11357878508878846, -0.10137697846011552], [-0.009850975273786157, 0.012388684934705838], [-0.06161841057716466, -0.08800746154276823], [0.14441250038314302, 0.03314472159469835], [0.0591917996425782, 0.004805795151051302], [0.013333276477477124, -0.09507749718241047], [0.17063655822896448, 0.04843759908226597], [-0.1344331819615861, -0.05922337335273136], [0.06208943499636459, -0.024062986382954482], [0.07367018291138853, -0.035779217947116373], [0.14585729013943718, 0.03009982534434381], [-4.325855833510748e-05, -0.028647035323512093], [0.14305140447270406, -0.023888872052471803], [-0.07976319741334352, -0.16482876245114228], [0.1885574626858104, 0.053870190769702474], [-0.05309493390479348, -0.043858603427681275], [-0.016396722417447277, -0.0762651776217721], [-0.05002987582879372, 0.013335850606603623], [-0.006182747725735604, -0.07399476858675702], [0.23399644684413393, 0.012991972872542812], [0.02482618313326541, -0.04195896218846199], [-0.128174938777414, -0.12066304391386172], [0.09817792256126145, 0.0345464968538372], [0.2662009106134194, 0.016853339572168485], [-0.08474308478864057, -0.08087212274889678], [-0.12134967006100011, -0.05517568806690888], [0.22120777322627516, 0.09285083315629342], [0.09236646913276327, -0.0008875670204694564], [0.1908995286085214, 0.05162086525571812], [-0.008062440362308243, -0.05784073691182215], [0.09972417042314631, -0.002203446781741257], [0.1901512971005631, 0.009834244862094546], [-0.04359919414199301, -0.08278536387370718], [0.14369639665916656, 0.03550218667286556], [0.17553071182792232, 0.061559809703634324], [0.22515277161715244, 0.016453676571411207], [-0.17664618558603268, -0.17750519061343661], [0.2316170081380341, 0.054953571669717934], [0.27568332895425074, 0.08938226559967045], [0.25107628654725844, 0.031115581307215777], [0.14009683195001182, 0.03533518650767815], [0.03224173476488553, 0.0327009275346384], [-0.030339588314953692, -0.018926821483012966], [0.246376957728387, 0.07080764698053299], [0.12041592545271677, -0.020814051448211725], [0.20965584870183582, 0.041976180371021715], [0.17347227142359004, 0.05961399151827855], [0.14648558030113445, 0.0739676310277816], [0.09210371850309602, 0.02559013761980081], [0.19014821093341658, 0.07169156367013144], [-0.11397329847646355, -0.025960539111311624], [0.13968537734755707, 0.036732735583895886], [0.002277830482019622, -0.0338369901563496], [0.2103548673400743, -0.00590835029437481], [0.07878832128688985, 0.04296170822683016], [0.11365045388628443, 0.04862276870252625], [0.1836789109960764, 0.06640737083935241], [0.25251147217059966, -0.04025065360745847], [0.29374048269147957, 0.1160187626454702], [0.2719594344140809, 0.07544186920622621], [0.2909367745043956, 0.10803935172081307], [0.32105534136803593, 0.1120916532277418], [0.3534600592560611, 0.10420433532575989], [0.1727337930584402, 0.07766510117192703], [0.2017785296295423, 0.11345077650476751], [0.22608196452163892, 0.0686461300090656], [0.11337462538967148, 0.04889214928618939], [0.15965491565231496, 0.07248526694356035], [0.1752700530307732, 0.06681182789101583], [0.20557384391327113, 0.09598509039356203], [0.17485290825546476, 0.036024314463164085], [0.14643405312233299, 0.08228887805042694], [0.19193077072819983, 0.012506499834891495], [0.15435138210852473, 0.02885932086036048], [0.13243534193771286, 0.024374538444317986], [0.2083396583557352, 0.04926249701532045], [0.1522641069792488, -6.622644039089187e-05], [0.42583832557834184, 0.12370982962991799], [0.28743980266613084, 0.07370503318355315], [0.1499827080043452, 0.05190092912655732], [0.04085501992593876, 0.044219869668621826], [0.2779039121067162, 0.014517628980508127], [0.2903544614669786, 0.10647055992755332], [0.16628952088167803, 0.06815719220721125], [-0.11312851306264295, -0.03794871228126706], [-0.11037810942047045, -0.04777058261117232], [-0.015158498351590392, -0.020233612090571697], [-0.5535222374298359, 0.8269171493771343], [-0.16550696202821272, 0.006732505502199735], [-0.09147795245073, -0.02371461104446701], [-0.5535222374298332, 0.8269171493771229], [0.23088578340386584, 0.10051686162255703], [-0.5535222374298332, 0.8269171493771229], [-0.5535222374298332, 0.8269171493771229], [0.10862516238603317, 0.03883459101338682], [-0.24342936882112343, -0.19753938791838657], [-0.22250167110064512, -0.13335198348222124], [-0.15182592055483476, -0.1370366194979494], [-0.16492629581372506, -0.1088283963745726], [-0.28160001000070667, -0.12577747347606977], [-0.2085847523934071, -0.07940048144590174], [-0.2629573392609211, -0.1256500496348997], [-0.15072098714394133, -0.11382814905236051], [-0.08085454178677572, -0.039213961051400625], [-0.16446542142847703, -0.12550530922592826], [-0.2783102635015961, -0.24253114934908157], [-0.3011355577413005, -0.19154576055309505], [-0.20483629127775935, -0.10873155978370957], [-0.22630922478488724, -0.10029078688485353], [-0.17074419965446475, -0.10828479420051196], [-0.2701169640093099, -0.145495427512595], [-0.26702798636382813, -0.11535954511852081], [-0.14572192827569572, -0.10683735028235139], [-0.12761349431013735, -0.08405176320600403], [-0.24348055008503, -0.13865118135252555], [-0.24118915812806652, -0.13026009057654192], [-0.2802210571307159, -0.1564983111453448], [-0.11422963118902614, -0.0475017761475203], [-0.19508663373837032, -0.11267459585775], [-0.10788315242420132, -0.1158872408191978], [-0.2476372326554792, -0.1341597937097613], [-0.2257394378559879, -0.09468890361946651], [-0.22412993799598666, -0.08220849351540115], [-0.1577484758665907, -0.08142125247315567], [-0.03181626201973692, -0.09421667866131972], [-0.20624162108825872, -0.18839921608584664], [-0.22704322873418292, -0.12896592138827961], [-0.17572618999231585, -0.09657545097798315], [-0.19981244499672987, -0.135724991678119], [-0.2759333236989523, -0.1198769315014235], [-0.2447279095912184, -0.13099878233976975], [-0.21037603484914394, -0.08291212439227755], [-0.1521788435317793, -0.09272358145477573], [-0.13552668775417, -0.09844349522520397], [-0.16046543366346935, -0.05842807310700702], [-0.17110789920593417, -0.07481482439600284], [-0.12493543181952861, -0.0461322243923116], [-0.002279805768340997, 0.0963933537674802]]}, "id": "el3011140133712973776"});
   }(mpld3);
}else if(typeof define === "function" && define.amd){
   // require.js is available: use it to load d3/mpld3
   require.config({paths: {d3: "https://mpld3.github.io/js/d3.v3.min"}});
   require(["d3"], function(d3){
      window.d3 = d3;
      mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
         
         mpld3.draw_figure("fig_el30111401337129737764893789309", {"axes": [{"xlim": [-0.80000000000000004, 0.60000000000000009], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "2 Princomps of Lovecraft TF-IDF Data", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 25.0, "position": [0.5, 1.0089605734767024], "rotation": -0.0, "id": "el3011140133712764880"}], "zoomable": true, "images": [], "xdomain": [-0.80000000000000004, 0.60000000000000009], "ylim": [-0.40000000000000002, 1.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el3011140133715543312", "ydomain": [-0.40000000000000002, 1.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el3011140133712439632", "pathtransforms": [[22.22222222222222, 0.0, 0.0, 22.22222222222222, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.3], "facecolors": ["#5CA3FF", "#2BD3FF", "#03FCFF", "#43BCFF", "#8579FF", "#E31BFF", "#E916FF", "#6798FF", "#A05FFF", "#CF30FF", "#1FE0FF", "#6D92FF", "#619EFF", "#BD41FF", "#718DFF", "#7E81FF", "#04FBFF", "#7B83FF", "#44BBFF", "#B748FF", "#CC32FF", "#BB44FF", "#24DBFF", "#49B5FF", "#926DFF", "#BC42FF", "#47B8FF", "#51ADFF", "#59A6FF", "#926DFF", "#BF40FF", "#43BCFF", "#639CFF", "#718EFF", "#59A6FF", "#CF30FF", "#DF20FF", "#8B74FF", "#CC32FF", "#34CBFF", "#20DFFF", "#639CFF", "#3FC0FF", "#DD21FF", "#D926FF", "#5FA0FF", "#38C6FF", "#38C7FF", "#DB24FF", "#59A6FF", "#F30BFF", "#6B93FF", "#04FBFF", "#E618FF", "#619DFF", "#45BAFF", "#2FD0FF", "#F20DFF", "#24DBFF", "#A05FFF", "#BE41FF", "#CB34FF", "#FE00FF", "#26D9FF", "#FB04FF", "#05FAFF", "#2CD3FF", "#748BFF", "#C738FF", "#D12EFF", "#FF00FF", "#01FEFF", "#1AE5FF", "#EA15FF", "#CC32FF", "#F20DFF", "#639CFF", "#BC42FF", "#1DE2FF", "#BD41FF", "#3AC5FF", "#758AFF", "#1DE2FF", "#6D92FF", "#6E91FF", "#C33BFF", "#8F70FF", "#26D9FF", "#7E81FF", "#8C72FF", "#916EFF", "#04FBFF", "#8A75FF", "#F906FF", "#1AE5FF", "#47B8FF", "#DF20FF", "#5FA0FF", "#718EFF", "#0AF5FF", "#E817FF", "#837BFF", "#738CFF", "#F708FF", "#AF50FF", "#649BFF", "#AD51FF", "#58A7FF", "#24DBFF", "#2ED1FF", "#718EFF", "#DD21FF", "#D02FFF", "#5FA0FF", "#1DE2FF", "#EE10FF", "#D926FF", "#C33CFF", "#46B9FF", "#0FF0FF", "#48B7FF", "#649BFF", "#BD41FF", "#C33CFF", "#1DE2FF", "#E718FF", "#609FFF", "#F608FF", "#758AFF", "#00FFFF", "#8778FF", "#18E7FF", "#7887FF", "#6996FF", "#22DDFF", "#738CFF", "#936BFF", "#FD01FF", "#45BAFF", "#C13EFF", "#A857FF", "#00FFFF", "#758AFF", "#CA35FF", "#EA15FF", "#03FCFF", "#A25DFF", "#ED11FF", "#8F70FF", "#10EFFF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 800.0, "width": 800.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Supernatural Horror in Literature with bibliography", "The Mystery of the Grave-Yard", "The Mysterious Ship", "The Little Glass Bottle", "The Beast in the Cave", "The Alchemist", "The Tomb", "Dagon", "A Reminiscence Of Dr. Samuel Johnson", "The Green Meadow with Winifred V. Jackson", "Polaris", "The Statement of Randolph Carter", "Memory", "Old Bugs", "The Doom That Came to Sarnath", "Beyond the Wall of Sleep", "The Transition of Juan Romero", "The White Ship", "The Picture in the House", "The Tree", "Nyarlathotep", "The Street", "The Temple", "The Terrible Old Man", "The Crawling Chaos with Elizabeth Berkeley", "Poetry and the Gods with Anna Helen Crofts", "From Beyond", "The Cats of Ulthar", "Ex Oblivione", "Facts Concerning the Late Arthur Jermyn and His Family", "Celephais", "The Outsider", "The Moon-Bog", "The Quest of Iranon", "The Music of Erich Zann", "The Nameless City", "The Other Gods", "Waste Paper", "Herbert West: Reanimator", "The Horror at Martin's Beach with Sonia H. Greene", "The Lurking Fear", "Azathoth", "The Hound", "Hypnos", "What the Moon Brings", "The Rats in the Walls", "The Unnamable", "The Festival", "Providence", "Imprisoned with the Pharaos", "The Shunned House", "He", "The Horror at Red Hook", "In The Vault", "<!-- -->At the Root  <!--", "The Call of Cthulhu", "The Strange High House in the Mist", "The Silver Key", "Pickman's Model", "Cool Air", "The Descendant", "The Case of Charles Dexter Ward", "The Despised Pastoral", "The Colour Out of Space", "The Thing in the Moonlight with J. Chapman Miske", "The Dream Quest of Unknown Kadath", "The Last Test with Adolphe de Castro", "The Curse of Yig with Zealia Bishop", "The Dunwich Horror", "Fungi from Yuggoth", "Medusa's Coil with Zealia Bishop", "The Mound with Zealia Bishop", "The Whisperer in Darkness", "The Shadow Over Innsmouth", "At the Mountains of Madness", "The Trap with Henry S. Whitehead", "The Man of Stone with Hazel Heald", "Dreams in the Witch-House", "The Horror in the Museum with Hazel Heald", "The Thing on the Doorstep", "Out of the Aeons with Hazel Heald", "Notes On Writing Weird Fiction", "Through the Gates of the Silver Key with E. Hoffmann Price", "The Winged Death with Hazel Heald", "The Book", "The Tree on the Hill with Duane W. Rimel", "The Challenge from Beyond with C. L. Moore, A. Merritt, Robert E. Howard, and Frank Belknap Long", "The Haunter Of The Dark", "Till A' the Seas with R. H. Barlow", "The Shadow Out of Time", "The Diary of Alonzo Typer with William Lumley", "The Disinterment with Duane W. Rimel", "The Horror in the Burying Ground with Hazel Heald", "The Night Ocean with R. H. Barlow", "Within The Walls Of Eryx with Kenneth Sterling", "The Evil Clergyman", "Ibid", "Sweet Ermengarde by Percy Simple", "The Very Old Folk", "Ashes with C. M. Eddy", "The Battle that Ended the Century with Robert Barlow", "Collapsing Cosmoses with Robert Barlow", "Deaf, Dumb, and Blind with C. M. Eddy", "The Electric Executioner with Adolphe de Castro", "The Ghost Eater with C. M. Eddy", "The Loved Dead with C. M. Eddy", "Two Black Bottles with Wilfred Blanch Talman", "An American to Mother England", "Astrophobos", "The Bride of the Sea", "The Cats", "Christmas Blessings", "Christmas Snows", "Christmastide", "The City", "The Conscript", "Despair", "To Edward John Moreton Drax Plunkett, Eighteenth Baron Dunsany", "Egyptian Christmas", "Fact and Fancy", "Festival", "The Garden", "Good Saint Nick", "Halcyon Days", "Hallowe'en in a Suburb", "The House", "Laeta; A Lament", "Lines on General Robert E. Lee", "Little Tiger", "The Messenger", "Nathanica", "Nemesis", "Ode for July Fourth, 1917", "On Receiving a Picture of Swans", "Pacifist War Song - 1917", "The Peace Advocate", "The Poe-ets Nightmare", "Poemata Minoria, Volume II", "The Rose of England", "On Reading Lord Dunsany's <i>Book of Wonder</i>", "Revelation", "St. John", "Sunset", "Tosh Bosh", "Where Once Poe Walked", "The Wood", "The Allowable Rhyme", "Cats and Dogs", "History of the Necronomicon", "Metrical Regularity"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el3011140133712439632"}], "data": {"data01": [[-0.1450877244248166, -0.012345432476003794], [-0.09581806267291283, -0.011097820110439183], [-0.14086914576745493, -0.023736819875285763], [-0.1901737728365357, -0.050740935125963955], [0.16248363598111987, 0.0469988322055736], [0.13896771892986473, 0.009198886379716909], [0.2052653732540268, 0.02914791590081186], [0.15795325772115862, -0.005467277709723869], [-0.08229437687259504, -0.008823667297106616], [0.15338138265019663, 0.00640114547686118], [-0.0011957655615174052, -0.08859784809117176], [0.08075139196725484, 0.014790235313773416], [-0.11357878508878846, -0.10137697846011552], [-0.009850975273786157, 0.012388684934705838], [-0.06161841057716466, -0.08800746154276823], [0.14441250038314302, 0.03314472159469835], [0.0591917996425782, 0.004805795151051302], [0.013333276477477124, -0.09507749718241047], [0.17063655822896448, 0.04843759908226597], [-0.1344331819615861, -0.05922337335273136], [0.06208943499636459, -0.024062986382954482], [0.07367018291138853, -0.035779217947116373], [0.14585729013943718, 0.03009982534434381], [-4.325855833510748e-05, -0.028647035323512093], [0.14305140447270406, -0.023888872052471803], [-0.07976319741334352, -0.16482876245114228], [0.1885574626858104, 0.053870190769702474], [-0.05309493390479348, -0.043858603427681275], [-0.016396722417447277, -0.0762651776217721], [-0.05002987582879372, 0.013335850606603623], [-0.006182747725735604, -0.07399476858675702], [0.23399644684413393, 0.012991972872542812], [0.02482618313326541, -0.04195896218846199], [-0.128174938777414, -0.12066304391386172], [0.09817792256126145, 0.0345464968538372], [0.2662009106134194, 0.016853339572168485], [-0.08474308478864057, -0.08087212274889678], [-0.12134967006100011, -0.05517568806690888], [0.22120777322627516, 0.09285083315629342], [0.09236646913276327, -0.0008875670204694564], [0.1908995286085214, 0.05162086525571812], [-0.008062440362308243, -0.05784073691182215], [0.09972417042314631, -0.002203446781741257], [0.1901512971005631, 0.009834244862094546], [-0.04359919414199301, -0.08278536387370718], [0.14369639665916656, 0.03550218667286556], [0.17553071182792232, 0.061559809703634324], [0.22515277161715244, 0.016453676571411207], [-0.17664618558603268, -0.17750519061343661], [0.2316170081380341, 0.054953571669717934], [0.27568332895425074, 0.08938226559967045], [0.25107628654725844, 0.031115581307215777], [0.14009683195001182, 0.03533518650767815], [0.03224173476488553, 0.0327009275346384], [-0.030339588314953692, -0.018926821483012966], [0.246376957728387, 0.07080764698053299], [0.12041592545271677, -0.020814051448211725], [0.20965584870183582, 0.041976180371021715], [0.17347227142359004, 0.05961399151827855], [0.14648558030113445, 0.0739676310277816], [0.09210371850309602, 0.02559013761980081], [0.19014821093341658, 0.07169156367013144], [-0.11397329847646355, -0.025960539111311624], [0.13968537734755707, 0.036732735583895886], [0.002277830482019622, -0.0338369901563496], [0.2103548673400743, -0.00590835029437481], [0.07878832128688985, 0.04296170822683016], [0.11365045388628443, 0.04862276870252625], [0.1836789109960764, 0.06640737083935241], [0.25251147217059966, -0.04025065360745847], [0.29374048269147957, 0.1160187626454702], [0.2719594344140809, 0.07544186920622621], [0.2909367745043956, 0.10803935172081307], [0.32105534136803593, 0.1120916532277418], [0.3534600592560611, 0.10420433532575989], [0.1727337930584402, 0.07766510117192703], [0.2017785296295423, 0.11345077650476751], [0.22608196452163892, 0.0686461300090656], [0.11337462538967148, 0.04889214928618939], [0.15965491565231496, 0.07248526694356035], [0.1752700530307732, 0.06681182789101583], [0.20557384391327113, 0.09598509039356203], [0.17485290825546476, 0.036024314463164085], [0.14643405312233299, 0.08228887805042694], [0.19193077072819983, 0.012506499834891495], [0.15435138210852473, 0.02885932086036048], [0.13243534193771286, 0.024374538444317986], [0.2083396583557352, 0.04926249701532045], [0.1522641069792488, -6.622644039089187e-05], [0.42583832557834184, 0.12370982962991799], [0.28743980266613084, 0.07370503318355315], [0.1499827080043452, 0.05190092912655732], [0.04085501992593876, 0.044219869668621826], [0.2779039121067162, 0.014517628980508127], [0.2903544614669786, 0.10647055992755332], [0.16628952088167803, 0.06815719220721125], [-0.11312851306264295, -0.03794871228126706], [-0.11037810942047045, -0.04777058261117232], [-0.015158498351590392, -0.020233612090571697], [-0.5535222374298359, 0.8269171493771343], [-0.16550696202821272, 0.006732505502199735], [-0.09147795245073, -0.02371461104446701], [-0.5535222374298332, 0.8269171493771229], [0.23088578340386584, 0.10051686162255703], [-0.5535222374298332, 0.8269171493771229], [-0.5535222374298332, 0.8269171493771229], [0.10862516238603317, 0.03883459101338682], [-0.24342936882112343, -0.19753938791838657], [-0.22250167110064512, -0.13335198348222124], [-0.15182592055483476, -0.1370366194979494], [-0.16492629581372506, -0.1088283963745726], [-0.28160001000070667, -0.12577747347606977], [-0.2085847523934071, -0.07940048144590174], [-0.2629573392609211, -0.1256500496348997], [-0.15072098714394133, -0.11382814905236051], [-0.08085454178677572, -0.039213961051400625], [-0.16446542142847703, -0.12550530922592826], [-0.2783102635015961, -0.24253114934908157], [-0.3011355577413005, -0.19154576055309505], [-0.20483629127775935, -0.10873155978370957], [-0.22630922478488724, -0.10029078688485353], [-0.17074419965446475, -0.10828479420051196], [-0.2701169640093099, -0.145495427512595], [-0.26702798636382813, -0.11535954511852081], [-0.14572192827569572, -0.10683735028235139], [-0.12761349431013735, -0.08405176320600403], [-0.24348055008503, -0.13865118135252555], [-0.24118915812806652, -0.13026009057654192], [-0.2802210571307159, -0.1564983111453448], [-0.11422963118902614, -0.0475017761475203], [-0.19508663373837032, -0.11267459585775], [-0.10788315242420132, -0.1158872408191978], [-0.2476372326554792, -0.1341597937097613], [-0.2257394378559879, -0.09468890361946651], [-0.22412993799598666, -0.08220849351540115], [-0.1577484758665907, -0.08142125247315567], [-0.03181626201973692, -0.09421667866131972], [-0.20624162108825872, -0.18839921608584664], [-0.22704322873418292, -0.12896592138827961], [-0.17572618999231585, -0.09657545097798315], [-0.19981244499672987, -0.135724991678119], [-0.2759333236989523, -0.1198769315014235], [-0.2447279095912184, -0.13099878233976975], [-0.21037603484914394, -0.08291212439227755], [-0.1521788435317793, -0.09272358145477573], [-0.13552668775417, -0.09844349522520397], [-0.16046543366346935, -0.05842807310700702], [-0.17110789920593417, -0.07481482439600284], [-0.12493543181952861, -0.0461322243923116], [-0.002279805768340997, 0.0963933537674802]]}, "id": "el3011140133712973776"});
      });
    });
}else{
    // require.js not available: dynamically load d3 & mpld3
    mpld3_load_lib("https://mpld3.github.io/js/d3.v3.min.js", function(){
         mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
                 
                 mpld3.draw_figure("fig_el30111401337129737764893789309", {"axes": [{"xlim": [-0.80000000000000004, 0.60000000000000009], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "2 Princomps of Lovecraft TF-IDF Data", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 25.0, "position": [0.5, 1.0089605734767024], "rotation": -0.0, "id": "el3011140133712764880"}], "zoomable": true, "images": [], "xdomain": [-0.80000000000000004, 0.60000000000000009], "ylim": [-0.40000000000000002, 1.0], "paths": [], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 9, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 9, "tickvalues": null}], "lines": [], "markers": [], "id": "el3011140133715543312", "ydomain": [-0.40000000000000002, 1.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data01", "yindex": 1, "id": "el3011140133712439632", "pathtransforms": [[22.22222222222222, 0.0, 0.0, 22.22222222222222, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.3], "facecolors": ["#5CA3FF", "#2BD3FF", "#03FCFF", "#43BCFF", "#8579FF", "#E31BFF", "#E916FF", "#6798FF", "#A05FFF", "#CF30FF", "#1FE0FF", "#6D92FF", "#619EFF", "#BD41FF", "#718DFF", "#7E81FF", "#04FBFF", "#7B83FF", "#44BBFF", "#B748FF", "#CC32FF", "#BB44FF", "#24DBFF", "#49B5FF", "#926DFF", "#BC42FF", "#47B8FF", "#51ADFF", "#59A6FF", "#926DFF", "#BF40FF", "#43BCFF", "#639CFF", "#718EFF", "#59A6FF", "#CF30FF", "#DF20FF", "#8B74FF", "#CC32FF", "#34CBFF", "#20DFFF", "#639CFF", "#3FC0FF", "#DD21FF", "#D926FF", "#5FA0FF", "#38C6FF", "#38C7FF", "#DB24FF", "#59A6FF", "#F30BFF", "#6B93FF", "#04FBFF", "#E618FF", "#619DFF", "#45BAFF", "#2FD0FF", "#F20DFF", "#24DBFF", "#A05FFF", "#BE41FF", "#CB34FF", "#FE00FF", "#26D9FF", "#FB04FF", "#05FAFF", "#2CD3FF", "#748BFF", "#C738FF", "#D12EFF", "#FF00FF", "#01FEFF", "#1AE5FF", "#EA15FF", "#CC32FF", "#F20DFF", "#639CFF", "#BC42FF", "#1DE2FF", "#BD41FF", "#3AC5FF", "#758AFF", "#1DE2FF", "#6D92FF", "#6E91FF", "#C33BFF", "#8F70FF", "#26D9FF", "#7E81FF", "#8C72FF", "#916EFF", "#04FBFF", "#8A75FF", "#F906FF", "#1AE5FF", "#47B8FF", "#DF20FF", "#5FA0FF", "#718EFF", "#0AF5FF", "#E817FF", "#837BFF", "#738CFF", "#F708FF", "#AF50FF", "#649BFF", "#AD51FF", "#58A7FF", "#24DBFF", "#2ED1FF", "#718EFF", "#DD21FF", "#D02FFF", "#5FA0FF", "#1DE2FF", "#EE10FF", "#D926FF", "#C33CFF", "#46B9FF", "#0FF0FF", "#48B7FF", "#649BFF", "#BD41FF", "#C33CFF", "#1DE2FF", "#E718FF", "#609FFF", "#F608FF", "#758AFF", "#00FFFF", "#8778FF", "#18E7FF", "#7887FF", "#6996FF", "#22DDFF", "#738CFF", "#936BFF", "#FD01FF", "#45BAFF", "#C13EFF", "#A857FF", "#00FFFF", "#758AFF", "#CA35FF", "#EA15FF", "#03FCFF", "#A25DFF", "#ED11FF", "#8F70FF", "#10EFFF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 800.0, "width": 800.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Supernatural Horror in Literature with bibliography", "The Mystery of the Grave-Yard", "The Mysterious Ship", "The Little Glass Bottle", "The Beast in the Cave", "The Alchemist", "The Tomb", "Dagon", "A Reminiscence Of Dr. Samuel Johnson", "The Green Meadow with Winifred V. Jackson", "Polaris", "The Statement of Randolph Carter", "Memory", "Old Bugs", "The Doom That Came to Sarnath", "Beyond the Wall of Sleep", "The Transition of Juan Romero", "The White Ship", "The Picture in the House", "The Tree", "Nyarlathotep", "The Street", "The Temple", "The Terrible Old Man", "The Crawling Chaos with Elizabeth Berkeley", "Poetry and the Gods with Anna Helen Crofts", "From Beyond", "The Cats of Ulthar", "Ex Oblivione", "Facts Concerning the Late Arthur Jermyn and His Family", "Celephais", "The Outsider", "The Moon-Bog", "The Quest of Iranon", "The Music of Erich Zann", "The Nameless City", "The Other Gods", "Waste Paper", "Herbert West: Reanimator", "The Horror at Martin's Beach with Sonia H. Greene", "The Lurking Fear", "Azathoth", "The Hound", "Hypnos", "What the Moon Brings", "The Rats in the Walls", "The Unnamable", "The Festival", "Providence", "Imprisoned with the Pharaos", "The Shunned House", "He", "The Horror at Red Hook", "In The Vault", "<!-- -->At the Root  <!--", "The Call of Cthulhu", "The Strange High House in the Mist", "The Silver Key", "Pickman's Model", "Cool Air", "The Descendant", "The Case of Charles Dexter Ward", "The Despised Pastoral", "The Colour Out of Space", "The Thing in the Moonlight with J. Chapman Miske", "The Dream Quest of Unknown Kadath", "The Last Test with Adolphe de Castro", "The Curse of Yig with Zealia Bishop", "The Dunwich Horror", "Fungi from Yuggoth", "Medusa's Coil with Zealia Bishop", "The Mound with Zealia Bishop", "The Whisperer in Darkness", "The Shadow Over Innsmouth", "At the Mountains of Madness", "The Trap with Henry S. Whitehead", "The Man of Stone with Hazel Heald", "Dreams in the Witch-House", "The Horror in the Museum with Hazel Heald", "The Thing on the Doorstep", "Out of the Aeons with Hazel Heald", "Notes On Writing Weird Fiction", "Through the Gates of the Silver Key with E. Hoffmann Price", "The Winged Death with Hazel Heald", "The Book", "The Tree on the Hill with Duane W. Rimel", "The Challenge from Beyond with C. L. Moore, A. Merritt, Robert E. Howard, and Frank Belknap Long", "The Haunter Of The Dark", "Till A' the Seas with R. H. Barlow", "The Shadow Out of Time", "The Diary of Alonzo Typer with William Lumley", "The Disinterment with Duane W. Rimel", "The Horror in the Burying Ground with Hazel Heald", "The Night Ocean with R. H. Barlow", "Within The Walls Of Eryx with Kenneth Sterling", "The Evil Clergyman", "Ibid", "Sweet Ermengarde by Percy Simple", "The Very Old Folk", "Ashes with C. M. Eddy", "The Battle that Ended the Century with Robert Barlow", "Collapsing Cosmoses with Robert Barlow", "Deaf, Dumb, and Blind with C. M. Eddy", "The Electric Executioner with Adolphe de Castro", "The Ghost Eater with C. M. Eddy", "The Loved Dead with C. M. Eddy", "Two Black Bottles with Wilfred Blanch Talman", "An American to Mother England", "Astrophobos", "The Bride of the Sea", "The Cats", "Christmas Blessings", "Christmas Snows", "Christmastide", "The City", "The Conscript", "Despair", "To Edward John Moreton Drax Plunkett, Eighteenth Baron Dunsany", "Egyptian Christmas", "Fact and Fancy", "Festival", "The Garden", "Good Saint Nick", "Halcyon Days", "Hallowe'en in a Suburb", "The House", "Laeta; A Lament", "Lines on General Robert E. Lee", "Little Tiger", "The Messenger", "Nathanica", "Nemesis", "Ode for July Fourth, 1917", "On Receiving a Picture of Swans", "Pacifist War Song - 1917", "The Peace Advocate", "The Poe-ets Nightmare", "Poemata Minoria, Volume II", "The Rose of England", "On Reading Lord Dunsany's <i>Book of Wonder</i>", "Revelation", "St. John", "Sunset", "Tosh Bosh", "Where Once Poe Walked", "The Wood", "The Allowable Rhyme", "Cats and Dogs", "History of the Necronomicon", "Metrical Regularity"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el3011140133712439632"}], "data": {"data01": [[-0.1450877244248166, -0.012345432476003794], [-0.09581806267291283, -0.011097820110439183], [-0.14086914576745493, -0.023736819875285763], [-0.1901737728365357, -0.050740935125963955], [0.16248363598111987, 0.0469988322055736], [0.13896771892986473, 0.009198886379716909], [0.2052653732540268, 0.02914791590081186], [0.15795325772115862, -0.005467277709723869], [-0.08229437687259504, -0.008823667297106616], [0.15338138265019663, 0.00640114547686118], [-0.0011957655615174052, -0.08859784809117176], [0.08075139196725484, 0.014790235313773416], [-0.11357878508878846, -0.10137697846011552], [-0.009850975273786157, 0.012388684934705838], [-0.06161841057716466, -0.08800746154276823], [0.14441250038314302, 0.03314472159469835], [0.0591917996425782, 0.004805795151051302], [0.013333276477477124, -0.09507749718241047], [0.17063655822896448, 0.04843759908226597], [-0.1344331819615861, -0.05922337335273136], [0.06208943499636459, -0.024062986382954482], [0.07367018291138853, -0.035779217947116373], [0.14585729013943718, 0.03009982534434381], [-4.325855833510748e-05, -0.028647035323512093], [0.14305140447270406, -0.023888872052471803], [-0.07976319741334352, -0.16482876245114228], [0.1885574626858104, 0.053870190769702474], [-0.05309493390479348, -0.043858603427681275], [-0.016396722417447277, -0.0762651776217721], [-0.05002987582879372, 0.013335850606603623], [-0.006182747725735604, -0.07399476858675702], [0.23399644684413393, 0.012991972872542812], [0.02482618313326541, -0.04195896218846199], [-0.128174938777414, -0.12066304391386172], [0.09817792256126145, 0.0345464968538372], [0.2662009106134194, 0.016853339572168485], [-0.08474308478864057, -0.08087212274889678], [-0.12134967006100011, -0.05517568806690888], [0.22120777322627516, 0.09285083315629342], [0.09236646913276327, -0.0008875670204694564], [0.1908995286085214, 0.05162086525571812], [-0.008062440362308243, -0.05784073691182215], [0.09972417042314631, -0.002203446781741257], [0.1901512971005631, 0.009834244862094546], [-0.04359919414199301, -0.08278536387370718], [0.14369639665916656, 0.03550218667286556], [0.17553071182792232, 0.061559809703634324], [0.22515277161715244, 0.016453676571411207], [-0.17664618558603268, -0.17750519061343661], [0.2316170081380341, 0.054953571669717934], [0.27568332895425074, 0.08938226559967045], [0.25107628654725844, 0.031115581307215777], [0.14009683195001182, 0.03533518650767815], [0.03224173476488553, 0.0327009275346384], [-0.030339588314953692, -0.018926821483012966], [0.246376957728387, 0.07080764698053299], [0.12041592545271677, -0.020814051448211725], [0.20965584870183582, 0.041976180371021715], [0.17347227142359004, 0.05961399151827855], [0.14648558030113445, 0.0739676310277816], [0.09210371850309602, 0.02559013761980081], [0.19014821093341658, 0.07169156367013144], [-0.11397329847646355, -0.025960539111311624], [0.13968537734755707, 0.036732735583895886], [0.002277830482019622, -0.0338369901563496], [0.2103548673400743, -0.00590835029437481], [0.07878832128688985, 0.04296170822683016], [0.11365045388628443, 0.04862276870252625], [0.1836789109960764, 0.06640737083935241], [0.25251147217059966, -0.04025065360745847], [0.29374048269147957, 0.1160187626454702], [0.2719594344140809, 0.07544186920622621], [0.2909367745043956, 0.10803935172081307], [0.32105534136803593, 0.1120916532277418], [0.3534600592560611, 0.10420433532575989], [0.1727337930584402, 0.07766510117192703], [0.2017785296295423, 0.11345077650476751], [0.22608196452163892, 0.0686461300090656], [0.11337462538967148, 0.04889214928618939], [0.15965491565231496, 0.07248526694356035], [0.1752700530307732, 0.06681182789101583], [0.20557384391327113, 0.09598509039356203], [0.17485290825546476, 0.036024314463164085], [0.14643405312233299, 0.08228887805042694], [0.19193077072819983, 0.012506499834891495], [0.15435138210852473, 0.02885932086036048], [0.13243534193771286, 0.024374538444317986], [0.2083396583557352, 0.04926249701532045], [0.1522641069792488, -6.622644039089187e-05], [0.42583832557834184, 0.12370982962991799], [0.28743980266613084, 0.07370503318355315], [0.1499827080043452, 0.05190092912655732], [0.04085501992593876, 0.044219869668621826], [0.2779039121067162, 0.014517628980508127], [0.2903544614669786, 0.10647055992755332], [0.16628952088167803, 0.06815719220721125], [-0.11312851306264295, -0.03794871228126706], [-0.11037810942047045, -0.04777058261117232], [-0.015158498351590392, -0.020233612090571697], [-0.5535222374298359, 0.8269171493771343], [-0.16550696202821272, 0.006732505502199735], [-0.09147795245073, -0.02371461104446701], [-0.5535222374298332, 0.8269171493771229], [0.23088578340386584, 0.10051686162255703], [-0.5535222374298332, 0.8269171493771229], [-0.5535222374298332, 0.8269171493771229], [0.10862516238603317, 0.03883459101338682], [-0.24342936882112343, -0.19753938791838657], [-0.22250167110064512, -0.13335198348222124], [-0.15182592055483476, -0.1370366194979494], [-0.16492629581372506, -0.1088283963745726], [-0.28160001000070667, -0.12577747347606977], [-0.2085847523934071, -0.07940048144590174], [-0.2629573392609211, -0.1256500496348997], [-0.15072098714394133, -0.11382814905236051], [-0.08085454178677572, -0.039213961051400625], [-0.16446542142847703, -0.12550530922592826], [-0.2783102635015961, -0.24253114934908157], [-0.3011355577413005, -0.19154576055309505], [-0.20483629127775935, -0.10873155978370957], [-0.22630922478488724, -0.10029078688485353], [-0.17074419965446475, -0.10828479420051196], [-0.2701169640093099, -0.145495427512595], [-0.26702798636382813, -0.11535954511852081], [-0.14572192827569572, -0.10683735028235139], [-0.12761349431013735, -0.08405176320600403], [-0.24348055008503, -0.13865118135252555], [-0.24118915812806652, -0.13026009057654192], [-0.2802210571307159, -0.1564983111453448], [-0.11422963118902614, -0.0475017761475203], [-0.19508663373837032, -0.11267459585775], [-0.10788315242420132, -0.1158872408191978], [-0.2476372326554792, -0.1341597937097613], [-0.2257394378559879, -0.09468890361946651], [-0.22412993799598666, -0.08220849351540115], [-0.1577484758665907, -0.08142125247315567], [-0.03181626201973692, -0.09421667866131972], [-0.20624162108825872, -0.18839921608584664], [-0.22704322873418292, -0.12896592138827961], [-0.17572618999231585, -0.09657545097798315], [-0.19981244499672987, -0.135724991678119], [-0.2759333236989523, -0.1198769315014235], [-0.2447279095912184, -0.13099878233976975], [-0.21037603484914394, -0.08291212439227755], [-0.1521788435317793, -0.09272358145477573], [-0.13552668775417, -0.09844349522520397], [-0.16046543366346935, -0.05842807310700702], [-0.17110789920593417, -0.07481482439600284], [-0.12493543181952861, -0.0461322243923116], [-0.002279805768340997, 0.0963933537674802]]}, "id": "el3011140133712973776"});
            })
         });
}
</script>



Neat plot. Ideally, it is here in 2 dimensions we could 'see' if any stories are
similiar. Works with similar terms should be clustered more near to each other.
Mouse over to see tool tips.  Also, The Love Dead With C. M. Eddy. I like to
think that because it was co authored it is different that the others

TSNE  for dimensional reduction, good write up here:
http://nbviewer.ipython.org/urls/gist.githubusercontent.com/AlexanderFabisch/1a0
c648de22eff4a2a3e/raw/59d5bc5ed8f8bfd9ff1f7faa749d1b095aa97d5a/t-SNE.ipynb

We can also use TSNE to reduce the dimensions. The above note book provides a
great overview. Again, just trying to reduce down to 2 dimensions for plotting


    from sklearn.decomposition import TruncatedSVD
    from sklearn.manifold import TSNE
    
    X_reduced = TruncatedSVD(n_components=50, random_state=0).fit_transform(X.todense())
    X_embedded = TSNE(n_components=2, perplexity=40, verbose=2).fit_transform(X_reduced)


    [t-SNE] Computing pairwise distances...
    [t-SNE] Computed conditional probabilities for sample 150 / 150
    [t-SNE] Mean sigma: 0.303010
    [t-SNE] Iteration 10: error = 15.6408568, gradient norm = 0.0683060
    [t-SNE] Iteration 20: error = 13.5020555, gradient norm = 0.0612151
    [t-SNE] Iteration 30: error = 14.2250906, gradient norm = 0.0886528
    [t-SNE] Iteration 32: did not make any progress during the last 30 episodes. Finished.
    [t-SNE] Iteration 40: error = 13.9255153, gradient norm = 0.0799449
    [t-SNE] Iteration 50: error = 13.4970054, gradient norm = 0.0870041
    [t-SNE] Iteration 60: error = 13.9179763, gradient norm = 0.0767198
    [t-SNE] Iteration 70: error = 13.7649049, gradient norm = 0.0775703
    [t-SNE] Iteration 80: error = 13.7250017, gradient norm = 0.0670308
    [t-SNE] Iteration 90: error = 14.2980674, gradient norm = 0.0670100
    [t-SNE] Iteration 100: error = 13.4276491, gradient norm = 0.0613550
    [t-SNE] Error after 100 iterations with early exaggeration: 13.427649
    [t-SNE] Iteration 110: error = 2.2979959, gradient norm = 0.0807588
    [t-SNE] Iteration 120: error = 2.2264473, gradient norm = 0.0103663
    [t-SNE] Iteration 130: error = 2.1736275, gradient norm = 0.0022691
    [t-SNE] Iteration 133: did not make any progress during the last 30 episodes. Finished.
    [t-SNE] Error after 133 iterations: 2.145785


TSNE Visualization Using Matplotlib and D3 via mpld3


    %matplotlib inline
    from sklearn.manifold import TSNE
    from sklearn.decomposition import TruncatedSVD
    
        
    fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'), figsize =(13,13))
    lables = df.title.values
    N = len(lables)
    t_x = X_embedded[:, 0]
    t_y = X_embedded[:, 1]
    scatter = ax.scatter(t_x,
                         t_y,
                         c=np.random.random(size=N),
                         alpha=0.3,
                         cmap=plt.cm.cool,
                         s = 490 )
    ax.grid(color='white', linestyle='solid')
    ax.set_title("TSNE of Lovecraft TF-IDF Data", size=25)
    labels = ['{0}'.format(title) for title in lables]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
    plt.axhspan(235, 178, color='turquoise', alpha=0.5)
    
    mpld3.display()
    #fig = figure(figsize=(15, 15))
    #plt.scatter(p_x,p_y,c=range(len(p_y)),cmap=cm.jet, s=300, marker="o", alpha = 0.5)






<style>

</style>

<div id="fig_el27871404686305758241813720432"></div>
<script>
function mpld3_load_lib(url, callback){
  var s = document.createElement('script');
  s.src = url;
  s.async = true;
  s.onreadystatechange = s.onload = callback;
  s.onerror = function(){console.warn("failed to load library " + url);};
  document.getElementsByTagName("head")[0].appendChild(s);
}

if(typeof(mpld3) !== "undefined" && mpld3._mpld3IsLoaded){
   // already loaded: just create the figure
   !function(mpld3){
       
       mpld3.draw_figure("fig_el27871404686305758241813720432", {"axes": [{"xlim": [-600.0, 600.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "TSNE of Lovecraft TF-IDF Data", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 25.0, "position": [0.5, 1.0068927488282327], "rotation": -0.0, "id": "el2787140468627070096"}], "zoomable": true, "images": [], "xdomain": [-600.0, 600.0], "ylim": [-500.0, 500.0], "paths": [{"edgecolor": "#40E0D0", "facecolor": "#40E0D0", "edgewidth": 1.0, "pathcodes": ["M", "L", "L", "L", "Z"], "yindex": 1, "coordinates": "display", "dasharray": "10,0", "zorder": 1, "alpha": 0.5, "xindex": 0, "data": "data01", "id": "el2787140468626853328"}], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 7, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 7, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468614152848", "ydomain": [-500.0, 500.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data02", "yindex": 1, "id": "el2787140468692973392", "pathtransforms": [[24.595492912420728, 0.0, 0.0, 24.595492912420728, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.3], "facecolors": ["#CE30FF", "#9D61FF", "#20DFFF", "#5EA1FF", "#D02FFF", "#916EFF", "#19E6FF", "#5EA1FF", "#3CC3FF", "#837CFF", "#D827FF", "#6E91FF", "#6D92FF", "#E817FF", "#936CFF", "#906FFF", "#41BEFF", "#9B64FF", "#936CFF", "#649BFF", "#FF00FF", "#E21DFF", "#C03FFF", "#8877FF", "#758AFF", "#2CD2FF", "#4CB3FF", "#C638FF", "#738CFF", "#E21DFF", "#23DCFF", "#817EFF", "#A559FF", "#837CFF", "#E31BFF", "#FE00FF", "#1BE4FF", "#1EE1FF", "#1EE1FF", "#AE51FF", "#5EA1FF", "#BC42FF", "#6699FF", "#A05FFF", "#C539FF", "#8B74FF", "#8976FF", "#13ECFF", "#6897FF", "#8B74FF", "#758AFF", "#E718FF", "#E916FF", "#D32CFF", "#5EA1FF", "#B748FF", "#639CFF", "#38C6FF", "#56A9FF", "#0FF0FF", "#53ACFF", "#758AFF", "#F509FF", "#4EB1FF", "#E817FF", "#38C7FF", "#2ED1FF", "#837BFF", "#AC52FF", "#08F7FF", "#36C9FF", "#738CFF", "#53ACFF", "#B649FF", "#827DFF", "#26D9FF", "#E618FF", "#49B6FF", "#BB44FF", "#C837FF", "#F708FF", "#7E81FF", "#9D61FF", "#54ABFF", "#AD51FF", "#758AFF", "#6F90FF", "#DB24FF", "#0AF5FF", "#E21DFF", "#DA25FF", "#807FFF", "#7C83FF", "#5BA3FF", "#FF00FF", "#19E6FF", "#9669FF", "#AE51FF", "#F00FFF", "#C837FF", "#A35BFF", "#1BE4FF", "#5EA1FF", "#20DEFF", "#E21DFF", "#C03FFF", "#C23DFF", "#A659FF", "#817EFF", "#24DBFF", "#51ADFF", "#20DFFF", "#B946FF", "#26D9FF", "#B34CFF", "#B14EFF", "#748BFF", "#20DFFF", "#4FB0FF", "#50AFFF", "#B34CFF", "#1AE5FF", "#D32BFF", "#C33CFF", "#2CD2FF", "#B847FF", "#AB54FF", "#BF40FF", "#2ED1FF", "#26D9FF", "#3AC5FF", "#5CA3FF", "#CB34FF", "#BD41FF", "#EE10FF", "#0CF3FF", "#00FFFF", "#B34CFF", "#45BAFF", "#54ABFF", "#8B74FF", "#17E8FF", "#A35BFF", "#51AEFF", "#A15EFF", "#D628FF", "#28D6FF", "#EF10FF", "#8778FF", "#ED11FF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 1040.0, "width": 1040.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Supernatural Horror in Literature with bibliography", "The Mystery of the Grave-Yard", "The Mysterious Ship", "The Little Glass Bottle", "The Beast in the Cave", "The Alchemist", "The Tomb", "Dagon", "A Reminiscence Of Dr. Samuel Johnson", "The Green Meadow with Winifred V. Jackson", "Polaris", "The Statement of Randolph Carter", "Memory", "Old Bugs", "The Doom That Came to Sarnath", "Beyond the Wall of Sleep", "The Transition of Juan Romero", "The White Ship", "The Picture in the House", "The Tree", "Nyarlathotep", "The Street", "The Temple", "The Terrible Old Man", "The Crawling Chaos with Elizabeth Berkeley", "Poetry and the Gods with Anna Helen Crofts", "From Beyond", "The Cats of Ulthar", "Ex Oblivione", "Facts Concerning the Late Arthur Jermyn and His Family", "Celephais", "The Outsider", "The Moon-Bog", "The Quest of Iranon", "The Music of Erich Zann", "The Nameless City", "The Other Gods", "Waste Paper", "Herbert West: Reanimator", "The Horror at Martin's Beach with Sonia H. Greene", "The Lurking Fear", "Azathoth", "The Hound", "Hypnos", "What the Moon Brings", "The Rats in the Walls", "The Unnamable", "The Festival", "Providence", "Imprisoned with the Pharaos", "The Shunned House", "He", "The Horror at Red Hook", "In The Vault", "<!-- -->At the Root  <!--", "The Call of Cthulhu", "The Strange High House in the Mist", "The Silver Key", "Pickman's Model", "Cool Air", "The Descendant", "The Case of Charles Dexter Ward", "The Despised Pastoral", "The Colour Out of Space", "The Thing in the Moonlight with J. Chapman Miske", "The Dream Quest of Unknown Kadath", "The Last Test with Adolphe de Castro", "The Curse of Yig with Zealia Bishop", "The Dunwich Horror", "Fungi from Yuggoth", "Medusa's Coil with Zealia Bishop", "The Mound with Zealia Bishop", "The Whisperer in Darkness", "The Shadow Over Innsmouth", "At the Mountains of Madness", "The Trap with Henry S. Whitehead", "The Man of Stone with Hazel Heald", "Dreams in the Witch-House", "The Horror in the Museum with Hazel Heald", "The Thing on the Doorstep", "Out of the Aeons with Hazel Heald", "Notes On Writing Weird Fiction", "Through the Gates of the Silver Key with E. Hoffmann Price", "The Winged Death with Hazel Heald", "The Book", "The Tree on the Hill with Duane W. Rimel", "The Challenge from Beyond with C. L. Moore, A. Merritt, Robert E. Howard, and Frank Belknap Long", "The Haunter Of The Dark", "Till A' the Seas with R. H. Barlow", "The Shadow Out of Time", "The Diary of Alonzo Typer with William Lumley", "The Disinterment with Duane W. Rimel", "The Horror in the Burying Ground with Hazel Heald", "The Night Ocean with R. H. Barlow", "Within The Walls Of Eryx with Kenneth Sterling", "The Evil Clergyman", "Ibid", "Sweet Ermengarde by Percy Simple", "The Very Old Folk", "Ashes with C. M. Eddy", "The Battle that Ended the Century with Robert Barlow", "Collapsing Cosmoses with Robert Barlow", "Deaf, Dumb, and Blind with C. M. Eddy", "The Electric Executioner with Adolphe de Castro", "The Ghost Eater with C. M. Eddy", "The Loved Dead with C. M. Eddy", "Two Black Bottles with Wilfred Blanch Talman", "An American to Mother England", "Astrophobos", "The Bride of the Sea", "The Cats", "Christmas Blessings", "Christmas Snows", "Christmastide", "The City", "The Conscript", "Despair", "To Edward John Moreton Drax Plunkett, Eighteenth Baron Dunsany", "Egyptian Christmas", "Fact and Fancy", "Festival", "The Garden", "Good Saint Nick", "Halcyon Days", "Hallowe'en in a Suburb", "The House", "Laeta; A Lament", "Lines on General Robert E. Lee", "Little Tiger", "The Messenger", "Nathanica", "Nemesis", "Ode for July Fourth, 1917", "On Receiving a Picture of Swans", "Pacifist War Song - 1917", "The Peace Advocate", "The Poe-ets Nightmare", "Poemata Minoria, Volume II", "The Rose of England", "On Reading Lord Dunsany's <i>Book of Wonder</i>", "Revelation", "St. John", "Sunset", "Tosh Bosh", "Where Once Poe Walked", "The Wood", "The Allowable Rhyme", "Cats and Dogs", "History of the Necronomicon", "Metrical Regularity"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692973392"}], "data": {"data02": [[58.52488644914431, 54.617324180508064], [-82.53020081273027, -44.306399432041175], [65.10969706002336, 23.671632130154315], [239.4665119443647, 244.38068172661383], [-9.100955048836749, 100.60195232543171], [112.03633090689803, 116.04250601147514], [-111.61360561892465, -88.37581356904809], [-11.286086363951686, 50.954419583807415], [-78.55225820692034, -23.659607812356363], [52.327357106415754, -48.505985839965], [315.16435291162117, -113.51234257531469], [-78.09982203521893, 58.11350654371594], [64.65264526937001, 167.0018399252153], [-133.7719762042119, -240.5222528005647], [-79.24125479655522, 40.089139019861676], [46.79407108680472, 24.307192327832112], [22.04422187067414, -52.04757392607371], [-19.373884955829386, 391.2964534995624], [-15.750043469740346, -17.032695826903954], [11.43169200263739, 70.32286950072123], [1.8728078115115159, -68.2327381913157], [-105.08391072034428, -16.012339927748396], [10.098002347051473, 30.44706517975904], [117.29263267626669, -32.877047980259896], [-172.69695052572536, 137.59501281795158], [38.14378943348946, -53.936797224384826], [13.044362585469433, 44.79384420724834], [-55.34494337760063, -283.333568568458], [-144.71383020077363, 225.9462580106215], [241.67643595097655, 142.20049985317033], [-48.99557382636017, 26.575487392903312], [42.0841747758688, -144.7454716408796], [-27.70213075505698, -7.375108779023952], [61.233234487399315, -36.29320918299199], [-7.827204834689472, -31.626558075618856], [14.898976776179142, 126.49657699618002], [437.88824063347437, 262.2376658558807], [6.65664323475676, -53.135293531945955], [-22.97449475422808, -58.811746241208745], [37.5113949343434, 57.76878593041498], [48.46638472915581, 74.15026495916827], [100.50573278100978, 74.97458372591925], [-54.662681033858895, 11.888599823044098], [-5.574949050720228, -6.902330618721646], [142.8218192399693, 3.501553494606938], [-125.27712249735957, 277.759049803489], [-35.33412396170478, 29.19752028588651], [77.46500727819469, -12.45798335032194], [-37.314345956508596, 8.051152244005285], [24.99223570996766, -4.972188293162198], [41.54036694910713, 115.63983971360065], [-44.54686815327678, 70.04681852960317], [-85.03409229259528, 118.63751757902433], [40.73188618839991, -6.323839418046858], [36.602845059501156, -73.54657855083889], [55.535955222623, -14.113372971365365], [24.666613997796958, 9.26406014540313], [-29.430078506035198, 59.63164653694049], [-63.488216521112264, -2.2795908339958806], [32.0260589087489, -93.9828227414968], [-26.423727035085868, -27.609229498927956], [38.13548364161684, 10.945680968603742], [-157.08592268899125, 38.582600287437906], [-1.069010881892173, 12.250835422920405], [86.78119259393566, 16.04047309335543], [-28.88915522363309, 121.06103825919821], [40.79705371229544, -24.409776438145364], [-59.74445805477252, 138.3788533727027], [-11.169805074617145, -192.5375340251483], [-42.297943262025626, 46.26144854584021], [60.562895688576255, -101.27049663470841], [70.11896678056331, 43.27986916297606], [79.5307393130438, 4.941036665530031], [-71.66722709085174, 11.85402392819903], [68.30373395863, 70.42769760173806], [-204.39988360653268, 59.888626159434146], [-112.75890748601314, 12.052710272215815], [-90.82617338865278, 7.847321930491323], [-61.31283569995636, -49.47766218610611], [-63.64431641798228, 70.36527155502385], [-0.9470208106739884, 80.97696300218445], [-22.634303126679768, 76.56581572823606], [47.7692195137583, 42.79237813711467], [-139.86627165217968, 337.9782232018276], [-6.405298447499491, 64.54297034108963], [-115.6291765066088, 89.97264445229571], [31.111384829319086, 28.04902716096539], [-52.88716903770467, 55.303903427111294], [102.91256203239239, 9.722563313605486], [-8.572083705134801, -49.087988861134534], [29.710096632107174, 100.0818831291558], [22.1851784473412, 61.38601692534276], [-174.41193439542297, -141.79750141631828], [75.21785884626021, -30.45394039750152], [281.17561495359433, 20.069946662595765], [80.87308262389715, -180.51291782456153], [-9.340355492906998, -85.03689868475391], [15.52367789203402, -283.74025641347316], [-106.09093551080905, -39.62461057446107], [-39.97719256780712, -20.17977642358774], [-77.27753019702722, -11.652175231817917], [127.32978380975845, -65.60943942285826], [-258.4177631720924, -368.17033617092983], [-39.62464963501912, -46.45858938453724], [-119.2932002351601, -62.19761269000391], [57.58436151432511, -78.35006919296524], [-30.188184120135013, -76.10864786601357], [-54.99416032031132, -33.051086471621254], [27.193709890792924, -21.988438041236737], [101.10145831373256, -249.7503340990291], [66.33939892125733, -60.87079250549243], [14.07092795795119, -16.34774833960751], [4.859605126787858, -21.42600258341161], [-23.65268405191915, -43.20292715013539], [-24.819896577087576, 16.027799928722438], [-1.1143450328753615, 115.2321075788319], [117.37320678869396, -82.68840583250454], [-30.98757593131982, -124.21249038978617], [-2.6836635346948046, 40.576512742908044], [80.41741550352965, -138.95980944646334], [33.680800152447084, -37.52000908072701], [-16.069595260708965, 28.763948502935886], [99.6818687146992, -19.639479540565347], [-25.654943569444967, 40.102941018713295], [-93.73137691533566, 91.01583439465865], [52.051581024579626, 8.091245813035517], [-86.69889415930263, 25.231267500287952], [-50.84213012256571, -65.95226586729946], [237.09872323392074, -141.73462117658818], [-143.67933411490532, -174.10595207135114], [13.662872350154675, -38.68244029167462], [119.90593804178346, 66.13182817749164], [-160.48424446746205, 78.30314866628487], [255.94037468346696, -225.62920835412544], [-71.61972095050481, -70.1310812247481], [-45.87871695922451, -3.425720769680582], [14.64007497127006, 17.61252231918489], [-56.30581317603183, -21.096754134107822], [64.54694265015291, -1.1010838556381162], [-71.36871554332623, -121.9930922172931], [10.112495644367577, 2.371938674841277], [-464.2702315957596, -71.60965818880737], [-35.21965093547504, 95.87186325825127], [-64.42314771302314, 31.05180143956652], [-4.456321171460635, 23.997032879517672], [28.463839633127822, 44.49186685402957], [84.99148406729624, 31.10675629353615], [-16.840790739838635, 4.4727370555905255], [-172.4810530264227, 170.80690248502208], [95.45654728648107, -48.54247229116445]], "data01": [[130.0, 722.4100000000001], [130.0, 676.4680000000001], [936.0, 676.4680000000001], [936.0, 722.4100000000001]]}, "id": "el2787140468630575824"});
   }(mpld3);
}else if(typeof define === "function" && define.amd){
   // require.js is available: use it to load d3/mpld3
   require.config({paths: {d3: "https://mpld3.github.io/js/d3.v3.min"}});
   require(["d3"], function(d3){
      window.d3 = d3;
      mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
         
         mpld3.draw_figure("fig_el27871404686305758241813720432", {"axes": [{"xlim": [-600.0, 600.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "TSNE of Lovecraft TF-IDF Data", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 25.0, "position": [0.5, 1.0068927488282327], "rotation": -0.0, "id": "el2787140468627070096"}], "zoomable": true, "images": [], "xdomain": [-600.0, 600.0], "ylim": [-500.0, 500.0], "paths": [{"edgecolor": "#40E0D0", "facecolor": "#40E0D0", "edgewidth": 1.0, "pathcodes": ["M", "L", "L", "L", "Z"], "yindex": 1, "coordinates": "display", "dasharray": "10,0", "zorder": 1, "alpha": 0.5, "xindex": 0, "data": "data01", "id": "el2787140468626853328"}], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 7, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 7, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468614152848", "ydomain": [-500.0, 500.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data02", "yindex": 1, "id": "el2787140468692973392", "pathtransforms": [[24.595492912420728, 0.0, 0.0, 24.595492912420728, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.3], "facecolors": ["#CE30FF", "#9D61FF", "#20DFFF", "#5EA1FF", "#D02FFF", "#916EFF", "#19E6FF", "#5EA1FF", "#3CC3FF", "#837CFF", "#D827FF", "#6E91FF", "#6D92FF", "#E817FF", "#936CFF", "#906FFF", "#41BEFF", "#9B64FF", "#936CFF", "#649BFF", "#FF00FF", "#E21DFF", "#C03FFF", "#8877FF", "#758AFF", "#2CD2FF", "#4CB3FF", "#C638FF", "#738CFF", "#E21DFF", "#23DCFF", "#817EFF", "#A559FF", "#837CFF", "#E31BFF", "#FE00FF", "#1BE4FF", "#1EE1FF", "#1EE1FF", "#AE51FF", "#5EA1FF", "#BC42FF", "#6699FF", "#A05FFF", "#C539FF", "#8B74FF", "#8976FF", "#13ECFF", "#6897FF", "#8B74FF", "#758AFF", "#E718FF", "#E916FF", "#D32CFF", "#5EA1FF", "#B748FF", "#639CFF", "#38C6FF", "#56A9FF", "#0FF0FF", "#53ACFF", "#758AFF", "#F509FF", "#4EB1FF", "#E817FF", "#38C7FF", "#2ED1FF", "#837BFF", "#AC52FF", "#08F7FF", "#36C9FF", "#738CFF", "#53ACFF", "#B649FF", "#827DFF", "#26D9FF", "#E618FF", "#49B6FF", "#BB44FF", "#C837FF", "#F708FF", "#7E81FF", "#9D61FF", "#54ABFF", "#AD51FF", "#758AFF", "#6F90FF", "#DB24FF", "#0AF5FF", "#E21DFF", "#DA25FF", "#807FFF", "#7C83FF", "#5BA3FF", "#FF00FF", "#19E6FF", "#9669FF", "#AE51FF", "#F00FFF", "#C837FF", "#A35BFF", "#1BE4FF", "#5EA1FF", "#20DEFF", "#E21DFF", "#C03FFF", "#C23DFF", "#A659FF", "#817EFF", "#24DBFF", "#51ADFF", "#20DFFF", "#B946FF", "#26D9FF", "#B34CFF", "#B14EFF", "#748BFF", "#20DFFF", "#4FB0FF", "#50AFFF", "#B34CFF", "#1AE5FF", "#D32BFF", "#C33CFF", "#2CD2FF", "#B847FF", "#AB54FF", "#BF40FF", "#2ED1FF", "#26D9FF", "#3AC5FF", "#5CA3FF", "#CB34FF", "#BD41FF", "#EE10FF", "#0CF3FF", "#00FFFF", "#B34CFF", "#45BAFF", "#54ABFF", "#8B74FF", "#17E8FF", "#A35BFF", "#51AEFF", "#A15EFF", "#D628FF", "#28D6FF", "#EF10FF", "#8778FF", "#ED11FF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 1040.0, "width": 1040.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Supernatural Horror in Literature with bibliography", "The Mystery of the Grave-Yard", "The Mysterious Ship", "The Little Glass Bottle", "The Beast in the Cave", "The Alchemist", "The Tomb", "Dagon", "A Reminiscence Of Dr. Samuel Johnson", "The Green Meadow with Winifred V. Jackson", "Polaris", "The Statement of Randolph Carter", "Memory", "Old Bugs", "The Doom That Came to Sarnath", "Beyond the Wall of Sleep", "The Transition of Juan Romero", "The White Ship", "The Picture in the House", "The Tree", "Nyarlathotep", "The Street", "The Temple", "The Terrible Old Man", "The Crawling Chaos with Elizabeth Berkeley", "Poetry and the Gods with Anna Helen Crofts", "From Beyond", "The Cats of Ulthar", "Ex Oblivione", "Facts Concerning the Late Arthur Jermyn and His Family", "Celephais", "The Outsider", "The Moon-Bog", "The Quest of Iranon", "The Music of Erich Zann", "The Nameless City", "The Other Gods", "Waste Paper", "Herbert West: Reanimator", "The Horror at Martin's Beach with Sonia H. Greene", "The Lurking Fear", "Azathoth", "The Hound", "Hypnos", "What the Moon Brings", "The Rats in the Walls", "The Unnamable", "The Festival", "Providence", "Imprisoned with the Pharaos", "The Shunned House", "He", "The Horror at Red Hook", "In The Vault", "<!-- -->At the Root  <!--", "The Call of Cthulhu", "The Strange High House in the Mist", "The Silver Key", "Pickman's Model", "Cool Air", "The Descendant", "The Case of Charles Dexter Ward", "The Despised Pastoral", "The Colour Out of Space", "The Thing in the Moonlight with J. Chapman Miske", "The Dream Quest of Unknown Kadath", "The Last Test with Adolphe de Castro", "The Curse of Yig with Zealia Bishop", "The Dunwich Horror", "Fungi from Yuggoth", "Medusa's Coil with Zealia Bishop", "The Mound with Zealia Bishop", "The Whisperer in Darkness", "The Shadow Over Innsmouth", "At the Mountains of Madness", "The Trap with Henry S. Whitehead", "The Man of Stone with Hazel Heald", "Dreams in the Witch-House", "The Horror in the Museum with Hazel Heald", "The Thing on the Doorstep", "Out of the Aeons with Hazel Heald", "Notes On Writing Weird Fiction", "Through the Gates of the Silver Key with E. Hoffmann Price", "The Winged Death with Hazel Heald", "The Book", "The Tree on the Hill with Duane W. Rimel", "The Challenge from Beyond with C. L. Moore, A. Merritt, Robert E. Howard, and Frank Belknap Long", "The Haunter Of The Dark", "Till A' the Seas with R. H. Barlow", "The Shadow Out of Time", "The Diary of Alonzo Typer with William Lumley", "The Disinterment with Duane W. Rimel", "The Horror in the Burying Ground with Hazel Heald", "The Night Ocean with R. H. Barlow", "Within The Walls Of Eryx with Kenneth Sterling", "The Evil Clergyman", "Ibid", "Sweet Ermengarde by Percy Simple", "The Very Old Folk", "Ashes with C. M. Eddy", "The Battle that Ended the Century with Robert Barlow", "Collapsing Cosmoses with Robert Barlow", "Deaf, Dumb, and Blind with C. M. Eddy", "The Electric Executioner with Adolphe de Castro", "The Ghost Eater with C. M. Eddy", "The Loved Dead with C. M. Eddy", "Two Black Bottles with Wilfred Blanch Talman", "An American to Mother England", "Astrophobos", "The Bride of the Sea", "The Cats", "Christmas Blessings", "Christmas Snows", "Christmastide", "The City", "The Conscript", "Despair", "To Edward John Moreton Drax Plunkett, Eighteenth Baron Dunsany", "Egyptian Christmas", "Fact and Fancy", "Festival", "The Garden", "Good Saint Nick", "Halcyon Days", "Hallowe'en in a Suburb", "The House", "Laeta; A Lament", "Lines on General Robert E. Lee", "Little Tiger", "The Messenger", "Nathanica", "Nemesis", "Ode for July Fourth, 1917", "On Receiving a Picture of Swans", "Pacifist War Song - 1917", "The Peace Advocate", "The Poe-ets Nightmare", "Poemata Minoria, Volume II", "The Rose of England", "On Reading Lord Dunsany's <i>Book of Wonder</i>", "Revelation", "St. John", "Sunset", "Tosh Bosh", "Where Once Poe Walked", "The Wood", "The Allowable Rhyme", "Cats and Dogs", "History of the Necronomicon", "Metrical Regularity"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692973392"}], "data": {"data02": [[58.52488644914431, 54.617324180508064], [-82.53020081273027, -44.306399432041175], [65.10969706002336, 23.671632130154315], [239.4665119443647, 244.38068172661383], [-9.100955048836749, 100.60195232543171], [112.03633090689803, 116.04250601147514], [-111.61360561892465, -88.37581356904809], [-11.286086363951686, 50.954419583807415], [-78.55225820692034, -23.659607812356363], [52.327357106415754, -48.505985839965], [315.16435291162117, -113.51234257531469], [-78.09982203521893, 58.11350654371594], [64.65264526937001, 167.0018399252153], [-133.7719762042119, -240.5222528005647], [-79.24125479655522, 40.089139019861676], [46.79407108680472, 24.307192327832112], [22.04422187067414, -52.04757392607371], [-19.373884955829386, 391.2964534995624], [-15.750043469740346, -17.032695826903954], [11.43169200263739, 70.32286950072123], [1.8728078115115159, -68.2327381913157], [-105.08391072034428, -16.012339927748396], [10.098002347051473, 30.44706517975904], [117.29263267626669, -32.877047980259896], [-172.69695052572536, 137.59501281795158], [38.14378943348946, -53.936797224384826], [13.044362585469433, 44.79384420724834], [-55.34494337760063, -283.333568568458], [-144.71383020077363, 225.9462580106215], [241.67643595097655, 142.20049985317033], [-48.99557382636017, 26.575487392903312], [42.0841747758688, -144.7454716408796], [-27.70213075505698, -7.375108779023952], [61.233234487399315, -36.29320918299199], [-7.827204834689472, -31.626558075618856], [14.898976776179142, 126.49657699618002], [437.88824063347437, 262.2376658558807], [6.65664323475676, -53.135293531945955], [-22.97449475422808, -58.811746241208745], [37.5113949343434, 57.76878593041498], [48.46638472915581, 74.15026495916827], [100.50573278100978, 74.97458372591925], [-54.662681033858895, 11.888599823044098], [-5.574949050720228, -6.902330618721646], [142.8218192399693, 3.501553494606938], [-125.27712249735957, 277.759049803489], [-35.33412396170478, 29.19752028588651], [77.46500727819469, -12.45798335032194], [-37.314345956508596, 8.051152244005285], [24.99223570996766, -4.972188293162198], [41.54036694910713, 115.63983971360065], [-44.54686815327678, 70.04681852960317], [-85.03409229259528, 118.63751757902433], [40.73188618839991, -6.323839418046858], [36.602845059501156, -73.54657855083889], [55.535955222623, -14.113372971365365], [24.666613997796958, 9.26406014540313], [-29.430078506035198, 59.63164653694049], [-63.488216521112264, -2.2795908339958806], [32.0260589087489, -93.9828227414968], [-26.423727035085868, -27.609229498927956], [38.13548364161684, 10.945680968603742], [-157.08592268899125, 38.582600287437906], [-1.069010881892173, 12.250835422920405], [86.78119259393566, 16.04047309335543], [-28.88915522363309, 121.06103825919821], [40.79705371229544, -24.409776438145364], [-59.74445805477252, 138.3788533727027], [-11.169805074617145, -192.5375340251483], [-42.297943262025626, 46.26144854584021], [60.562895688576255, -101.27049663470841], [70.11896678056331, 43.27986916297606], [79.5307393130438, 4.941036665530031], [-71.66722709085174, 11.85402392819903], [68.30373395863, 70.42769760173806], [-204.39988360653268, 59.888626159434146], [-112.75890748601314, 12.052710272215815], [-90.82617338865278, 7.847321930491323], [-61.31283569995636, -49.47766218610611], [-63.64431641798228, 70.36527155502385], [-0.9470208106739884, 80.97696300218445], [-22.634303126679768, 76.56581572823606], [47.7692195137583, 42.79237813711467], [-139.86627165217968, 337.9782232018276], [-6.405298447499491, 64.54297034108963], [-115.6291765066088, 89.97264445229571], [31.111384829319086, 28.04902716096539], [-52.88716903770467, 55.303903427111294], [102.91256203239239, 9.722563313605486], [-8.572083705134801, -49.087988861134534], [29.710096632107174, 100.0818831291558], [22.1851784473412, 61.38601692534276], [-174.41193439542297, -141.79750141631828], [75.21785884626021, -30.45394039750152], [281.17561495359433, 20.069946662595765], [80.87308262389715, -180.51291782456153], [-9.340355492906998, -85.03689868475391], [15.52367789203402, -283.74025641347316], [-106.09093551080905, -39.62461057446107], [-39.97719256780712, -20.17977642358774], [-77.27753019702722, -11.652175231817917], [127.32978380975845, -65.60943942285826], [-258.4177631720924, -368.17033617092983], [-39.62464963501912, -46.45858938453724], [-119.2932002351601, -62.19761269000391], [57.58436151432511, -78.35006919296524], [-30.188184120135013, -76.10864786601357], [-54.99416032031132, -33.051086471621254], [27.193709890792924, -21.988438041236737], [101.10145831373256, -249.7503340990291], [66.33939892125733, -60.87079250549243], [14.07092795795119, -16.34774833960751], [4.859605126787858, -21.42600258341161], [-23.65268405191915, -43.20292715013539], [-24.819896577087576, 16.027799928722438], [-1.1143450328753615, 115.2321075788319], [117.37320678869396, -82.68840583250454], [-30.98757593131982, -124.21249038978617], [-2.6836635346948046, 40.576512742908044], [80.41741550352965, -138.95980944646334], [33.680800152447084, -37.52000908072701], [-16.069595260708965, 28.763948502935886], [99.6818687146992, -19.639479540565347], [-25.654943569444967, 40.102941018713295], [-93.73137691533566, 91.01583439465865], [52.051581024579626, 8.091245813035517], [-86.69889415930263, 25.231267500287952], [-50.84213012256571, -65.95226586729946], [237.09872323392074, -141.73462117658818], [-143.67933411490532, -174.10595207135114], [13.662872350154675, -38.68244029167462], [119.90593804178346, 66.13182817749164], [-160.48424446746205, 78.30314866628487], [255.94037468346696, -225.62920835412544], [-71.61972095050481, -70.1310812247481], [-45.87871695922451, -3.425720769680582], [14.64007497127006, 17.61252231918489], [-56.30581317603183, -21.096754134107822], [64.54694265015291, -1.1010838556381162], [-71.36871554332623, -121.9930922172931], [10.112495644367577, 2.371938674841277], [-464.2702315957596, -71.60965818880737], [-35.21965093547504, 95.87186325825127], [-64.42314771302314, 31.05180143956652], [-4.456321171460635, 23.997032879517672], [28.463839633127822, 44.49186685402957], [84.99148406729624, 31.10675629353615], [-16.840790739838635, 4.4727370555905255], [-172.4810530264227, 170.80690248502208], [95.45654728648107, -48.54247229116445]], "data01": [[130.0, 722.4100000000001], [130.0, 676.4680000000001], [936.0, 676.4680000000001], [936.0, 722.4100000000001]]}, "id": "el2787140468630575824"});
      });
    });
}else{
    // require.js not available: dynamically load d3 & mpld3
    mpld3_load_lib("https://mpld3.github.io/js/d3.v3.min.js", function(){
         mpld3_load_lib("https://mpld3.github.io/js/mpld3.v0.2.js", function(){
                 
                 mpld3.draw_figure("fig_el27871404686305758241813720432", {"axes": [{"xlim": [-600.0, 600.0], "yscale": "linear", "axesbg": "#EEEEEE", "texts": [{"v_baseline": "auto", "h_anchor": "middle", "color": "#000000", "text": "TSNE of Lovecraft TF-IDF Data", "coordinates": "axes", "zorder": 3, "alpha": 1, "fontsize": 25.0, "position": [0.5, 1.0068927488282327], "rotation": -0.0, "id": "el2787140468627070096"}], "zoomable": true, "images": [], "xdomain": [-600.0, 600.0], "ylim": [-500.0, 500.0], "paths": [{"edgecolor": "#40E0D0", "facecolor": "#40E0D0", "edgewidth": 1.0, "pathcodes": ["M", "L", "L", "L", "Z"], "yindex": 1, "coordinates": "display", "dasharray": "10,0", "zorder": 1, "alpha": 0.5, "xindex": 0, "data": "data01", "id": "el2787140468626853328"}], "sharey": [], "sharex": [], "axesbgalpha": null, "axes": [{"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "bottom", "nticks": 7, "tickvalues": null}, {"scale": "linear", "tickformat": null, "grid": {"color": "#FFFFFF", "alpha": 1.0, "dasharray": "10,0", "gridOn": true}, "fontsize": 10.0, "position": "left", "nticks": 7, "tickvalues": null}], "lines": [], "markers": [], "id": "el2787140468614152848", "ydomain": [-500.0, 500.0], "collections": [{"paths": [[[[0.0, -0.5], [0.13260155, -0.5], [0.25978993539242673, -0.44731684579412084], [0.3535533905932738, -0.3535533905932738], [0.44731684579412084, -0.25978993539242673], [0.5, -0.13260155], [0.5, 0.0], [0.5, 0.13260155], [0.44731684579412084, 0.25978993539242673], [0.3535533905932738, 0.3535533905932738], [0.25978993539242673, 0.44731684579412084], [0.13260155, 0.5], [0.0, 0.5], [-0.13260155, 0.5], [-0.25978993539242673, 0.44731684579412084], [-0.3535533905932738, 0.3535533905932738], [-0.44731684579412084, 0.25978993539242673], [-0.5, 0.13260155], [-0.5, 0.0], [-0.5, -0.13260155], [-0.44731684579412084, -0.25978993539242673], [-0.3535533905932738, -0.3535533905932738], [-0.25978993539242673, -0.44731684579412084], [-0.13260155, -0.5], [0.0, -0.5]], ["M", "C", "C", "C", "C", "C", "C", "C", "C", "Z"]]], "edgecolors": ["#000000"], "edgewidths": [1.0], "offsets": "data02", "yindex": 1, "id": "el2787140468692973392", "pathtransforms": [[24.595492912420728, 0.0, 0.0, 24.595492912420728, 0.0, 0.0]], "pathcoordinates": "display", "offsetcoordinates": "data", "zorder": 1, "xindex": 0, "alphas": [0.3], "facecolors": ["#CE30FF", "#9D61FF", "#20DFFF", "#5EA1FF", "#D02FFF", "#916EFF", "#19E6FF", "#5EA1FF", "#3CC3FF", "#837CFF", "#D827FF", "#6E91FF", "#6D92FF", "#E817FF", "#936CFF", "#906FFF", "#41BEFF", "#9B64FF", "#936CFF", "#649BFF", "#FF00FF", "#E21DFF", "#C03FFF", "#8877FF", "#758AFF", "#2CD2FF", "#4CB3FF", "#C638FF", "#738CFF", "#E21DFF", "#23DCFF", "#817EFF", "#A559FF", "#837CFF", "#E31BFF", "#FE00FF", "#1BE4FF", "#1EE1FF", "#1EE1FF", "#AE51FF", "#5EA1FF", "#BC42FF", "#6699FF", "#A05FFF", "#C539FF", "#8B74FF", "#8976FF", "#13ECFF", "#6897FF", "#8B74FF", "#758AFF", "#E718FF", "#E916FF", "#D32CFF", "#5EA1FF", "#B748FF", "#639CFF", "#38C6FF", "#56A9FF", "#0FF0FF", "#53ACFF", "#758AFF", "#F509FF", "#4EB1FF", "#E817FF", "#38C7FF", "#2ED1FF", "#837BFF", "#AC52FF", "#08F7FF", "#36C9FF", "#738CFF", "#53ACFF", "#B649FF", "#827DFF", "#26D9FF", "#E618FF", "#49B6FF", "#BB44FF", "#C837FF", "#F708FF", "#7E81FF", "#9D61FF", "#54ABFF", "#AD51FF", "#758AFF", "#6F90FF", "#DB24FF", "#0AF5FF", "#E21DFF", "#DA25FF", "#807FFF", "#7C83FF", "#5BA3FF", "#FF00FF", "#19E6FF", "#9669FF", "#AE51FF", "#F00FFF", "#C837FF", "#A35BFF", "#1BE4FF", "#5EA1FF", "#20DEFF", "#E21DFF", "#C03FFF", "#C23DFF", "#A659FF", "#817EFF", "#24DBFF", "#51ADFF", "#20DFFF", "#B946FF", "#26D9FF", "#B34CFF", "#B14EFF", "#748BFF", "#20DFFF", "#4FB0FF", "#50AFFF", "#B34CFF", "#1AE5FF", "#D32BFF", "#C33CFF", "#2CD2FF", "#B847FF", "#AB54FF", "#BF40FF", "#2ED1FF", "#26D9FF", "#3AC5FF", "#5CA3FF", "#CB34FF", "#BD41FF", "#EE10FF", "#0CF3FF", "#00FFFF", "#B34CFF", "#45BAFF", "#54ABFF", "#8B74FF", "#17E8FF", "#A35BFF", "#51AEFF", "#A15EFF", "#D628FF", "#28D6FF", "#EF10FF", "#8778FF", "#ED11FF"]}], "xscale": "linear", "bbox": [0.125, 0.125, 0.77500000000000002, 0.77500000000000002]}], "height": 1040.0, "width": 1040.0, "plugins": [{"type": "reset"}, {"enabled": false, "button": true, "type": "zoom"}, {"enabled": false, "button": true, "type": "boxzoom"}, {"voffset": 10, "labels": ["Supernatural Horror in Literature with bibliography", "The Mystery of the Grave-Yard", "The Mysterious Ship", "The Little Glass Bottle", "The Beast in the Cave", "The Alchemist", "The Tomb", "Dagon", "A Reminiscence Of Dr. Samuel Johnson", "The Green Meadow with Winifred V. Jackson", "Polaris", "The Statement of Randolph Carter", "Memory", "Old Bugs", "The Doom That Came to Sarnath", "Beyond the Wall of Sleep", "The Transition of Juan Romero", "The White Ship", "The Picture in the House", "The Tree", "Nyarlathotep", "The Street", "The Temple", "The Terrible Old Man", "The Crawling Chaos with Elizabeth Berkeley", "Poetry and the Gods with Anna Helen Crofts", "From Beyond", "The Cats of Ulthar", "Ex Oblivione", "Facts Concerning the Late Arthur Jermyn and His Family", "Celephais", "The Outsider", "The Moon-Bog", "The Quest of Iranon", "The Music of Erich Zann", "The Nameless City", "The Other Gods", "Waste Paper", "Herbert West: Reanimator", "The Horror at Martin's Beach with Sonia H. Greene", "The Lurking Fear", "Azathoth", "The Hound", "Hypnos", "What the Moon Brings", "The Rats in the Walls", "The Unnamable", "The Festival", "Providence", "Imprisoned with the Pharaos", "The Shunned House", "He", "The Horror at Red Hook", "In The Vault", "<!-- -->At the Root  <!--", "The Call of Cthulhu", "The Strange High House in the Mist", "The Silver Key", "Pickman's Model", "Cool Air", "The Descendant", "The Case of Charles Dexter Ward", "The Despised Pastoral", "The Colour Out of Space", "The Thing in the Moonlight with J. Chapman Miske", "The Dream Quest of Unknown Kadath", "The Last Test with Adolphe de Castro", "The Curse of Yig with Zealia Bishop", "The Dunwich Horror", "Fungi from Yuggoth", "Medusa's Coil with Zealia Bishop", "The Mound with Zealia Bishop", "The Whisperer in Darkness", "The Shadow Over Innsmouth", "At the Mountains of Madness", "The Trap with Henry S. Whitehead", "The Man of Stone with Hazel Heald", "Dreams in the Witch-House", "The Horror in the Museum with Hazel Heald", "The Thing on the Doorstep", "Out of the Aeons with Hazel Heald", "Notes On Writing Weird Fiction", "Through the Gates of the Silver Key with E. Hoffmann Price", "The Winged Death with Hazel Heald", "The Book", "The Tree on the Hill with Duane W. Rimel", "The Challenge from Beyond with C. L. Moore, A. Merritt, Robert E. Howard, and Frank Belknap Long", "The Haunter Of The Dark", "Till A' the Seas with R. H. Barlow", "The Shadow Out of Time", "The Diary of Alonzo Typer with William Lumley", "The Disinterment with Duane W. Rimel", "The Horror in the Burying Ground with Hazel Heald", "The Night Ocean with R. H. Barlow", "Within The Walls Of Eryx with Kenneth Sterling", "The Evil Clergyman", "Ibid", "Sweet Ermengarde by Percy Simple", "The Very Old Folk", "Ashes with C. M. Eddy", "The Battle that Ended the Century with Robert Barlow", "Collapsing Cosmoses with Robert Barlow", "Deaf, Dumb, and Blind with C. M. Eddy", "The Electric Executioner with Adolphe de Castro", "The Ghost Eater with C. M. Eddy", "The Loved Dead with C. M. Eddy", "Two Black Bottles with Wilfred Blanch Talman", "An American to Mother England", "Astrophobos", "The Bride of the Sea", "The Cats", "Christmas Blessings", "Christmas Snows", "Christmastide", "The City", "The Conscript", "Despair", "To Edward John Moreton Drax Plunkett, Eighteenth Baron Dunsany", "Egyptian Christmas", "Fact and Fancy", "Festival", "The Garden", "Good Saint Nick", "Halcyon Days", "Hallowe'en in a Suburb", "The House", "Laeta; A Lament", "Lines on General Robert E. Lee", "Little Tiger", "The Messenger", "Nathanica", "Nemesis", "Ode for July Fourth, 1917", "On Receiving a Picture of Swans", "Pacifist War Song - 1917", "The Peace Advocate", "The Poe-ets Nightmare", "Poemata Minoria, Volume II", "The Rose of England", "On Reading Lord Dunsany's <i>Book of Wonder</i>", "Revelation", "St. John", "Sunset", "Tosh Bosh", "Where Once Poe Walked", "The Wood", "The Allowable Rhyme", "Cats and Dogs", "History of the Necronomicon", "Metrical Regularity"], "hoffset": 0, "location": "mouse", "type": "tooltip", "id": "el2787140468692973392"}], "data": {"data02": [[58.52488644914431, 54.617324180508064], [-82.53020081273027, -44.306399432041175], [65.10969706002336, 23.671632130154315], [239.4665119443647, 244.38068172661383], [-9.100955048836749, 100.60195232543171], [112.03633090689803, 116.04250601147514], [-111.61360561892465, -88.37581356904809], [-11.286086363951686, 50.954419583807415], [-78.55225820692034, -23.659607812356363], [52.327357106415754, -48.505985839965], [315.16435291162117, -113.51234257531469], [-78.09982203521893, 58.11350654371594], [64.65264526937001, 167.0018399252153], [-133.7719762042119, -240.5222528005647], [-79.24125479655522, 40.089139019861676], [46.79407108680472, 24.307192327832112], [22.04422187067414, -52.04757392607371], [-19.373884955829386, 391.2964534995624], [-15.750043469740346, -17.032695826903954], [11.43169200263739, 70.32286950072123], [1.8728078115115159, -68.2327381913157], [-105.08391072034428, -16.012339927748396], [10.098002347051473, 30.44706517975904], [117.29263267626669, -32.877047980259896], [-172.69695052572536, 137.59501281795158], [38.14378943348946, -53.936797224384826], [13.044362585469433, 44.79384420724834], [-55.34494337760063, -283.333568568458], [-144.71383020077363, 225.9462580106215], [241.67643595097655, 142.20049985317033], [-48.99557382636017, 26.575487392903312], [42.0841747758688, -144.7454716408796], [-27.70213075505698, -7.375108779023952], [61.233234487399315, -36.29320918299199], [-7.827204834689472, -31.626558075618856], [14.898976776179142, 126.49657699618002], [437.88824063347437, 262.2376658558807], [6.65664323475676, -53.135293531945955], [-22.97449475422808, -58.811746241208745], [37.5113949343434, 57.76878593041498], [48.46638472915581, 74.15026495916827], [100.50573278100978, 74.97458372591925], [-54.662681033858895, 11.888599823044098], [-5.574949050720228, -6.902330618721646], [142.8218192399693, 3.501553494606938], [-125.27712249735957, 277.759049803489], [-35.33412396170478, 29.19752028588651], [77.46500727819469, -12.45798335032194], [-37.314345956508596, 8.051152244005285], [24.99223570996766, -4.972188293162198], [41.54036694910713, 115.63983971360065], [-44.54686815327678, 70.04681852960317], [-85.03409229259528, 118.63751757902433], [40.73188618839991, -6.323839418046858], [36.602845059501156, -73.54657855083889], [55.535955222623, -14.113372971365365], [24.666613997796958, 9.26406014540313], [-29.430078506035198, 59.63164653694049], [-63.488216521112264, -2.2795908339958806], [32.0260589087489, -93.9828227414968], [-26.423727035085868, -27.609229498927956], [38.13548364161684, 10.945680968603742], [-157.08592268899125, 38.582600287437906], [-1.069010881892173, 12.250835422920405], [86.78119259393566, 16.04047309335543], [-28.88915522363309, 121.06103825919821], [40.79705371229544, -24.409776438145364], [-59.74445805477252, 138.3788533727027], [-11.169805074617145, -192.5375340251483], [-42.297943262025626, 46.26144854584021], [60.562895688576255, -101.27049663470841], [70.11896678056331, 43.27986916297606], [79.5307393130438, 4.941036665530031], [-71.66722709085174, 11.85402392819903], [68.30373395863, 70.42769760173806], [-204.39988360653268, 59.888626159434146], [-112.75890748601314, 12.052710272215815], [-90.82617338865278, 7.847321930491323], [-61.31283569995636, -49.47766218610611], [-63.64431641798228, 70.36527155502385], [-0.9470208106739884, 80.97696300218445], [-22.634303126679768, 76.56581572823606], [47.7692195137583, 42.79237813711467], [-139.86627165217968, 337.9782232018276], [-6.405298447499491, 64.54297034108963], [-115.6291765066088, 89.97264445229571], [31.111384829319086, 28.04902716096539], [-52.88716903770467, 55.303903427111294], [102.91256203239239, 9.722563313605486], [-8.572083705134801, -49.087988861134534], [29.710096632107174, 100.0818831291558], [22.1851784473412, 61.38601692534276], [-174.41193439542297, -141.79750141631828], [75.21785884626021, -30.45394039750152], [281.17561495359433, 20.069946662595765], [80.87308262389715, -180.51291782456153], [-9.340355492906998, -85.03689868475391], [15.52367789203402, -283.74025641347316], [-106.09093551080905, -39.62461057446107], [-39.97719256780712, -20.17977642358774], [-77.27753019702722, -11.652175231817917], [127.32978380975845, -65.60943942285826], [-258.4177631720924, -368.17033617092983], [-39.62464963501912, -46.45858938453724], [-119.2932002351601, -62.19761269000391], [57.58436151432511, -78.35006919296524], [-30.188184120135013, -76.10864786601357], [-54.99416032031132, -33.051086471621254], [27.193709890792924, -21.988438041236737], [101.10145831373256, -249.7503340990291], [66.33939892125733, -60.87079250549243], [14.07092795795119, -16.34774833960751], [4.859605126787858, -21.42600258341161], [-23.65268405191915, -43.20292715013539], [-24.819896577087576, 16.027799928722438], [-1.1143450328753615, 115.2321075788319], [117.37320678869396, -82.68840583250454], [-30.98757593131982, -124.21249038978617], [-2.6836635346948046, 40.576512742908044], [80.41741550352965, -138.95980944646334], [33.680800152447084, -37.52000908072701], [-16.069595260708965, 28.763948502935886], [99.6818687146992, -19.639479540565347], [-25.654943569444967, 40.102941018713295], [-93.73137691533566, 91.01583439465865], [52.051581024579626, 8.091245813035517], [-86.69889415930263, 25.231267500287952], [-50.84213012256571, -65.95226586729946], [237.09872323392074, -141.73462117658818], [-143.67933411490532, -174.10595207135114], [13.662872350154675, -38.68244029167462], [119.90593804178346, 66.13182817749164], [-160.48424446746205, 78.30314866628487], [255.94037468346696, -225.62920835412544], [-71.61972095050481, -70.1310812247481], [-45.87871695922451, -3.425720769680582], [14.64007497127006, 17.61252231918489], [-56.30581317603183, -21.096754134107822], [64.54694265015291, -1.1010838556381162], [-71.36871554332623, -121.9930922172931], [10.112495644367577, 2.371938674841277], [-464.2702315957596, -71.60965818880737], [-35.21965093547504, 95.87186325825127], [-64.42314771302314, 31.05180143956652], [-4.456321171460635, 23.997032879517672], [28.463839633127822, 44.49186685402957], [84.99148406729624, 31.10675629353615], [-16.840790739838635, 4.4727370555905255], [-172.4810530264227, 170.80690248502208], [95.45654728648107, -48.54247229116445]], "data01": [[130.0, 722.4100000000001], [130.0, 676.4680000000001], [936.0, 676.4680000000001], [936.0, 722.4100000000001]]}, "id": "el2787140468630575824"});
            })
         });
}
</script>



Again with the C.M. Eddy stories...

We can now find the highest scored words with TF-IDF

Anyrate -- we can take a work and find the top tfidf words. These are the
important words to a story, and, they are kinda neat when you see them
(especially if you know the work).

Like these highest weighted words --


    dtm.ix['At the Mountains of Madness'].order(ascending=False)[:10]




    danforth    0.215768
    lake        0.211862
    one         0.168938
    us          0.167903
    antarct     0.138937
    camp        0.137232
    sculptur    0.131495
    plane       0.123398
    could       0.118929
    mountain    0.115847
    Name: At the Mountains of Madness, dtype: float64



Here is a quick summary of 'At the Mountains of Madness'  -- Geologist William
Dyer goes to __Antacrtica__ and  discovers 'horrific ruines and a dangereous
secrets beyond a range of mountains higher than the Himalayas'. Professor
__Lake__ discoveres an ancient race of lifeforms known as the 'Old __Ones__'.
Neat right?

Here is another --


    dtm.ix['The Call of Cthulhu'].order(ascending=False)[:10]




    johansen     0.274319
    legrass      0.233679
    wilcox       0.225270
    cult         0.208972
    professor    0.202079
    uncl         0.177877
    cthulhu      0.158113
    dream        0.145855
    one          0.124678
    angel        0.120953
    Name: The Call of Cthulhu, dtype: float64



Quick summary of Call of Cthulhu -The texts narrator 'recounts his discovery of
notes left behind by his __uncle__', and linguistics __professor__. People are
dreamin' super scary dreams artists are making super scary art. One artists
,__Wilcox__, creates a horrible bas-relief sculpture "which the narrator
describes: 'My somewhat extravagant imagination yielded simultaneous pictures of
an octopus, a dragon, and a human caricature.... A pulpy, tentacled head
surmounted a grotesque and scaly body with rudimentary wings'"We begin to also
hear the tale of inspector __Legrasse__ about a  statuette composed of an
unidentifiable greenish-black stone, 'captured some months before in the wooded
swamps south of New Orleans during a raid on a supposed voodoo [__cult__]
meeting'". The tale crescendos with the account of a derelict ship of which the
only survivor is __johansen__.  Johansen and ilk land on ancient city raised
from the bottom of the sea, open a  "monstrously carven portal",
they release __Cthulhu__:

###"It lumbered slobberingly into sight and gropingly squeezed Its gelatinous
green immensity through the black doorway.... The stars were right again, and
what an age-old cult had failed to do by design, a band of innocent sailors had
done by accident. After vigintillions of years great Cthulhu was loose again,
and ravening for delight".###



