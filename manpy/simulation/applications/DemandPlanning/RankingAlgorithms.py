# ===========================================================================
# Copyright 2015 Dublin City University
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================

"""
Created on 29 Jan 2015

@author: Anna
"""
from operator import itemgetter
from numpy import mean, random


# elitist selection with linear ranking completion
def rankingElitist(candidates, elg):

    if elg >= len(
        candidates
    ):  # it always picks even number of chromosomes for crossover in order to have required pair of parents for crossover in LS
        elg = elg - elg % 2
    else:
        elg = elg + elg % 2

    # in original implementation final candidates are generated by eliminating duplicate solutions
    finalCandidates = candidates

    # add order sequence to candidates
    for i in range(len(finalCandidates)):
        finalCandidates[i]["orderSequence"] = i

    # sort candidates
    fittestLateness = sorted(
        finalCandidates, key=itemgetter("excess", "lateness", "earliness")
    )
    fittestUtilisation = sorted(
        finalCandidates, key=itemgetter("targetUtil", "minUtil")
    )

    Both = sorted(
        finalCandidates,
        key=itemgetter("excess", "lateness", "targetUtil", "minUtil", "earliness"),
    )
    bestC = Both[0]

    # ============================
    # first sorting criterion
    # ============================
    # select candidates that appear in the first positions in both lists...with preference on Lateness metrics
    numTop = elg  # int(math.ceil(len(finalCandidates)*0.2))
    aLateness = []
    aUtilisation = []
    for i in range(numTop):
        aLateness.append(fittestLateness[i]["orderSequence"])
        aUtilisation.append(fittestUtilisation[i]["orderSequence"])

    aLateness = set(aLateness)
    aUtilisation = set(aUtilisation)
    selection = list(aLateness.intersection(aUtilisation))

    fittest = []
    fitID = []
    numFit = min([len(selection), elg])

    for i in range(numFit):
        x = 0
        while x < numTop:
            if fittestLateness[x]["orderSequence"] == selection[i]:
                fittest.append(fittestLateness[x])
                fitID.append(fittestLateness[x]["orderSequence"])
                break
            x += 1

    # other ranking option for elitist selection
    #    i = 0
    #    x = 0
    #    if numFit < elg:
    #        while i < elg-numFit:
    #            while x<len(fittestLateness):
    #                if fittestLateness[x]['orderSequence'] not in fitID:
    #                    fittest.append(fittestLateness[x])
    #                    fitID.append(fittestLateness[x]['orderSequence'])
    #                    i+=1
    #                    break
    #                x+=1

    # ==========================
    # second sorting criterion
    # ==========================
    # if there is not enough ants in selection then calculate the average ranking between the two sorted lists and
    # select the ants with highest average ranking not previously included
    # solve the ties in favour of lateness...ranking is also done to complete the selection with linear ranking
    ultRanking = {}
    rankingList = []
    for i in range(len(fittestLateness)):
        ultRanking[fittestLateness[i]["orderSequence"]] = {
            "lateness": i,
            "orderSequence": fittestLateness[i]["orderSequence"],
        }
    for i in range(len(fittestUtilisation)):
        ultRanking[fittestUtilisation[i]["orderSequence"]]["utilisation"] = i
        ultRanking[fittestUtilisation[i]["orderSequence"]]["avg"] = mean(
            [
                ultRanking[fittestUtilisation[i]["orderSequence"]]["utilisation"],
                ultRanking[fittestUtilisation[i]["orderSequence"]]["lateness"],
            ]
        )
        rankingList.append(ultRanking[fittestUtilisation[i]["orderSequence"]])

    rankingList = sorted(rankingList, key=itemgetter("avg", "lateness"))

    # add the best solutions to the elitist list until the number of chromosomes specified in the selection parameters is reached
    for i in range(len(rankingList)):

        if numFit == elg:
            break

        if rankingList[i]["orderSequence"] not in fitID:

            x = 0
            while x < len(fittestLateness):
                if (
                    fittestLateness[x]["orderSequence"]
                    == rankingList[i]["orderSequence"]
                ):
                    fittest.append(fittestLateness[x])
                    fitID.append(fittestLateness[x]["orderSequence"])
                    break
                x += 1

            numFit += 1

    # ======================
    # start linear ranking
    # ======================

    # create the probability list
    numCand = len(candidates)
    s = [0 for i in range(numCand)]

    # assuming a linear ranking parameter equal to 2, complete the probability list...see matlab files as reference
    for i in range(numCand - 2, -1, -1):
        s[i] = s[i + 1] + (1.0 / numCand) * (
            0.2 + 1.6 * float(numCand - 1 - i) / (numCand - 1)
        )  # (2.0/numCand)*float(numCand-1-i)/(numCand-1)

    for i in range(numCand - elg):
        # randomly generate probability of selection
        probSel = random.random() * float(s[0])

        # find chromosome that corresponds to that probability
        chromosome = numCand - 1
        while chromosome >= 0 and s[chromosome] < probSel:
            chromosome -= 1

        x = 0
        while x < len(fittestLateness):
            if (
                fittestLateness[x]["orderSequence"]
                == rankingList[chromosome]["orderSequence"]
            ):
                fittest.append(fittestLateness[x])
                fitID.append(fittestLateness[x]["orderSequence"])
                break
            x += 1

    return fittest, bestC


# compares best chromosomes and suggest to terminate if the best one does not change
def compareChromosomes(bestChromosome, termination):

    if len(bestChromosome) < termination:
        return False

    for chrom in range(len(bestChromosome) - 2, len(bestChromosome) - termination, -1):
        if (
            bestChromosome[chrom + 1]["excess"] != bestChromosome[chrom]["excess"]
            or bestChromosome[chrom + 1]["lateness"]
            != bestChromosome[chrom]["lateness"]
            or bestChromosome[chrom + 1]["earliness"]
            != bestChromosome[chrom]["earliness"]
            or bestChromosome[chrom + 1]["targetUtil"]
            != bestChromosome[chrom]["targetUtil"]
            or bestChromosome[chrom + 1]["minUtil"] != bestChromosome[chrom]["minUtil"]
        ):

            return False

    return True


# choose final solution based on first
def finalRanking(finalCandidates):

    # add order sequence to candidates
    for i in range(len(finalCandidates)):
        finalCandidates[i]["orderSequence"] = i

    # sort candidates
    fittestLateness = sorted(
        finalCandidates,
        key=itemgetter("excess", "lateness", "targetUtil", "minUtil", "earliness"),
    )

    return fittestLateness[0]
