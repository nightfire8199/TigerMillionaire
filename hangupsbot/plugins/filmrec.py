import plugins
import asyncio
import csv
from collections import defaultdict
from math import sqrt
import random

def initialise(bot):
    plugins.register_user_command(["filmrec"], ["filmrate"])
    plugins.register_admin_command(['filmload'])

    if not bot.memory.exists(['filmrec']):
        print("INITIALIZING")
        bot.memory.set_by_path(['filmrec'], {})
        with open("ratings.csv") as csvfile:
            rateread = csv.reader(csvfile)
            for row in rateread:
                ratings[str(row[0])][row[1]] = row[2]
 
        with open("movies.csv") as csvfile:
            filmread = csv.reader(csvfile)
            for row in filmread:
                movies[str(row[0])] = row[1]
        bot.memory.get_by_path(['filmrec'])["ratings"] = ratings
        bot.memory.get_by_path(['filmrec'])["movies"] = movies


def pearson(data, p1, p2):
    sim = {}
    for item in data[p1]:
        if item in data[p2]: sim[item] = 1
    
    n = float(len(sim))

    if n==0: return 0

    sum1=sum([float(data[p1][it]) for it in sim])
    sum2=sum([float(data[p2][it]) for it in sim])

    sum1Sq=sum([pow(float(data[p1][it]),2) for it in sim])
    sum2Sq=sum([pow(float(data[p2][it]),2) for it in sim])

    pSum=sum([float(data[p1][it])*float(data[p2][it]) for it in sim])

    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0

    r=num/den
    return r

def reccomend(data, p1):    
    if len(data[p1].keys()) < 2:
        print("Error: Insufficient data")
        print("Try reviewing some of these: ")
        recc = reccomend(data, "1")
        for film in recc[0:5]:
                print(str(film[1])+": " + movies[film[1]])
        return []
    totals = {}
    simSums = {}
    for other in data:
        if other == p1: continue
        sim = pearson(data, p1, other)
        if sim <=0: continue
        for item in data[other]:
            if item not in data[p1] or float(data[p1][item])==0:
                totals.setdefault(item,0)
                totals[item]+=float(data[other][item])*sim

                simSums.setdefault(item,0)
                simSums[item]+=sim

        rankings=[(total/simSums[item],item) for item,total in totals.items()]
        

        rankings.sort()
        rankings.reverse()
        return rankings

def filmrate(bot, event, film, score, *args):
    ratings = bot.memory.get_by_path(['filmrec']).get("ratings")
    movies = bot.memory.get_by_path(['filmrec']).get("movies")
    if film not in movies.keys():
        yield from bot.coro_send_message(event.conv, _("FilmID: {} not found").format(film))
    else:
        ratings[event.user_id][film] = score
        bot.memory.get_by_path(['filmrec'])["ratings"] = ratings
        yield from bot.coro_send_message(event.conv, _("Rating added by <b>{}</b> for {}").format(event.user.full_name, movies[film]))

def filmload(bot, event, *args):
    ratings = defaultdict(dict)
    movies = {}
    bot.memory.set_by_path(['filmrec'], {}) 
    with open("plugins/ratings.csv") as csvfile:
        rateread = csv.reader(csvfile)
        for row in rateread:
            ratings[str(row[0])][row[1]] = row[2]
    with open("plugins/movies.csv") as csvfile:
        filmread = csv.reader(csvfile)
        for row in filmread:
            movies[str(row[0])] = row[1]
    bot.memory.get_by_path(['filmrec'])["ratings"] = ratings
    bot.memory.get_by_path(['filmrec'])["movies"] = movies
    yield from bot.coro_send_message(event.conv, _("Film Data Sucessfully loaded, <b>{}</b> ratings for <b>{}</b> movies").format(len(ratings.keys()), len(movies.keys())))    

def filmrec(bot, event, *args):
    """
    A film reccomendation service for hangoutsbot

    <b>/bot filmrec</b>
    Will create a list of reccomended films based off the user's taste profile.
    Remember the FilmID! You'll need it when rating the film
    (Note: Must review two films before customized results will begin appearing)

    <b>/bot filmrate <i><filmID> <rating (0-5)></i></b>
    Will rate the film with filmID on a scale from 0-5, decimals allowed
    """
    ratings = bot.memory.get_by_path(['filmrec']).get("ratings")
    movies = bot.memory.get_by_path(['filmrec']).get("movies")
    filmlist = ""
    if len(ratings[event.user_id].keys()) < 2:
        recc = reccomend(ratings, "1")
        reccshuff = random.sample(recc[0:20],5)
        for film in reccshuff:
                filmlist += str(film[1])+": " + str(movies[film[1]]) + "\n"
        yield from bot.coro_send_message(event.conv, _("You have not reviewed enough films, try reviewing some of these: {} type <i>/bot help filmrec</i> for assistance").format("\n" + filmlist + "\n"))
    else:
        recc = reccomend(ratings, event.user_id)
        reccshuff = random.sample(recc[0:50],5)
        for film in reccshuff:
            filmlist += str(film[1])+": " + movies[film[1]] + " -- Est Rating: " + "%.1f" % film[0] + "\n\n"
        yield from bot.coro_send_message(event.conv, _("{}").format(filmlist))
