# This Python file uses the following encoding: utf-8

from pprint import pprint
from math import sqrt


# 该数据总共四列，共分为用户ID、电影ID、用户评分、时间
# 以用户名为key的字典，格式为{用户:{电影:评分,电影:评分}}
def make_data():
    result = {}
    f = open('data/u.data', 'r')
    lines = f.readlines()
    for line in lines:
        # 按行分割数据
        (userId, itemId, score, time) = line.strip().split("\t")
        # 字典要提前定义
        if not result.has_key(userId):
            result[userId] = {}
        # 注意float,不然后续的运算存在类型问题
        result[userId][itemId] = float(score)
    return result


# 将id替换为电影名 构成数据集
def loadMovieLens(path='data'):
    # Get movie titles
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # Load data
    prefs = {}
    for line in open(path + '/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)
    return prefs


# critics = make_data()
critics = {
    'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                  'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                  'The Night Listener': 3.0},

    'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                     'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 3.5},

    'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                         'Superman Returns': 3.5, 'The Night Listener': 4.0},

    'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                     'The Night Listener': 4.5, 'Superman Returns': 4.0,
                     'You, Me and Dupree': 2.5},

    'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                     'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 2.0},

    'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                      'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},

    'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


# 欧几里得距离
# 但在实际应用中，我们希望相似度越大返回的值越大，并且控制在0~1之间的值。
# 为此，我们可以取函数值加1的倒数(加1是为了防止除0的情况)：
def sim_distance(prefs, person1, person2):
    si = {}
    for itemId in prefs[person1]:
        if itemId in prefs[person2]:
            si[itemId] = 1
    # no same item
    if len(si) == 0: return 0
    sum_of_squares = 0.0

    # 计算距离
    # for item in si:
    #    sum_of_squares =  pow(prefs[person1][item] - prefs[person2][item],2) + sum_of_squares
    # sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in si])
    return 1 / (1 + sqrt(sum_of_squares))


# 皮尔逊相关度
# 介于 1 和 -1 之间的值，其中，1 表示变量完全正相关， 0 表示无关，-1 表示完全负相关。
# 负相关怎么产生的不是很清楚 这里干脆抛弃算了
def sim_pearson(prefs, p1, p2):
    si = {}  # 这里不用字典 用队列好像更方便
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    if len(si) == 0: return 0

    n = len(si)

    # 计算开始
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    # 计算结束

    if den == 0: return 0
    r = num / den
    return r


# 推荐用户
def topMatches(prefs, person, n=5, similarity=sim_distance):
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


# 基于用户推荐物品      user_based
# 计算其他用户对某个Toby没看过电影的加权和来得到总权重，
# 最后除以相似度和，是为了防止某一电影被看过的多，总和会更多的影响，也称“归一化”处理。
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}

    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs, person, other)
        # 去除负相关的用户
        if sim <= 0: continue
        for item in prefs[other]:
            if item in prefs[person]: continue
            totals.setdefault(item, 0)
            totals[item] += sim * prefs[other][item]
            simSums.setdefault(item, 0)
            simSums[item] += sim
    rankings = [(totals[item] / simSums[item], item) for item in totals]
    # rankings=[(total/simSums[item],item) for item,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


# 基于物品的列表 item_based
# 以物品为key的字典，格式为{电影:{用户:评分,用户:评分}}
def transformPrefs(prefs):
    itemList = {}
    for person in prefs:
        for item in prefs[person]:
            if not itemList.has_key(item):
                itemList[item] = {}
                # result.setdefault(item,{})
            itemList[item][person] = prefs[person][item]
    return itemList


# 构建基于物品相似度数据集
# 物品间相似的变化不会像人那么频繁，所以我们可以构造物品间相似的集合，存成文件重复利用
def calculateSimilarItems(prefs, n=10):
    result = {}
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        c += 1
        if c % 10 == 0: print("{0:d}/{1:d}".format(c, len(itemPrefs)))
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


# 构建基于人的相似度数据集
def calculateSimilarUsers(prefs, n=10):
    result = {}
    c = 0
    for user in prefs:
        c += 1
        if c % 10 == 0: print("{0:d}/{1:d}".format(c, len(prefs)))
        scores = topMatches(prefs, user, n=n, similarity=sim_distance)
        result[user] = scores
    return result


# 基于物品的推荐
def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings: continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    rankings = [(score / totalSim[item], item) for item, score in scores.items()]

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings


# 测试
# print sim_distance( critics,'Lisa Rose', 'Gene Seymour')
# print sim_pearson( critics,'Lisa Rose', 'Gene Seymour')
print(topMatches(critics, 'Lisa Rose', 10))

# res = getRecommendations( critics , 'Michael Phillips')
# print res

# print len(transformPrefs( critics ))
# 基于物品推荐
# res = calculateSimilarItems( critics )
# print getRecommendedItems( critics,res,'2')
# 基于泰坦尼克号的相关电影的推荐
# res = transformPrefs( critics )
# print getRecommendations( res , '313')
# 格式化数据 载入电影名 构建数据集
# print loadMovieLens()
# 构建人相关度列表 对比时间
res = calculateSimilarUsers(critics)
# pprint(res)

