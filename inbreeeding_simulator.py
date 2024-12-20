from collections import Counter
from enum import Enum
import pandas as pd
import numpy as np
import argparse
import random
import csv

class PoolType(Enum):
    father_mother = 1
    father_ca = 2
    mother_ca= 3
    within_ca= 4

def setLimit(max_mean, total_ind):
    limits = {}
    for elem in range(1,total_ind+1):
        limits[elem]= np.random.poisson(max_mean)

    return limits

def checkToLimitAddToList(parent_occurrences, new_generation, parent1_idx, parent2_idx, num_children, founder_male, founder_female, limit_dic):
    parent_key1 = parent1_idx
    parent_key2 = parent2_idx
    max1= limit_dic.get(parent_key1)
    max2= limit_dic.get(parent_key2)
    if parent_occurrences.get(parent_key1, 0)+num_children < max1 and parent_occurrences.get(parent_key2, 0) + num_children < max2 :
        parent_occurrences[parent_key1] = parent_occurrences.get(parent_key1, 0) + num_children
        parent_occurrences[parent_key2] = parent_occurrences.get(parent_key2, 0) + num_children
        if parent_occurrences[parent_key1] > max1:
            founder_male.remove(parent_key1)
        if parent_occurrences[parent_key2] > max2: 
            founder_female.remove(parent_key2)

        offspring = [f"{parent1_idx}-{parent2_idx}" for _ in range(num_children)]
        new_generation.extend(offspring)


def createFounders(male_number, start):
    founder_male = [i for i in range(1+start, male_number+1+start)]
    return founder_male

def createSourcePopulation(female, male, migration_rate):
    mig = round(migration_rate*(female+male))
    source_pool = [i for i in range(female+male+1, female+male+1+mig)]
    return source_pool

def simulatePopulation(male_number, female_number, num_generations, seed, mean_children_per_couple, max_child_mean, rep, migration_rate, memo):
    np.random.seed(seed)
    pop_size = female_number + male_number
    pop_sim_matrix = np.empty((1, pop_size), dtype=object) 
    mig = round((female_number+male_number)*migration_rate)
    founder_female = createFounders(female_number, male_number)
    founder_male = createFounders(male_number,0)
    migration_pool = createSourcePopulation(female_number, male_number, migration_rate)


    for generation in range(num_generations):
        new_generation = []
        parent_occurrences = {}  # Dictionary to store parent indexes and their occurrences
        founder_female = createFounders(female_number, male_number)
        founder_male = createFounders(male_number,0)
        for i in range(len(migration_pool)):
            if i+1 > mig//2:
                founder_female.append(migration_pool[i])
            else:
                founder_male.append(migration_pool[i])
        limit_dic = setLimit(max_child_mean, male_number+female_number+mig)


        while len(new_generation) < pop_size:
            isSibling= (1,2)
            if generation == 0: 
                parent1_idx = np.random.choice(founder_male)
                parent2_idx = np.random.choice(founder_female)
            elif generation > 0:
                while len(isSibling) != 0:
                    parent1_idx = np.random.choice(founder_male)
                    parent2_idx = np.random.choice(founder_female)
                    if parent1_idx <= male_number + female_number and parent2_idx <= male_number + female_number:
                        isSibling = set((pop_sim_matrix[generation-1][parent1_idx-1]).split("-")) & set((pop_sim_matrix[generation-1][parent2_idx-1]).split("-"))
                    else:
                        break
                # Use Poisson distribution to determine the number of children for this couple
            num_children = np.random.poisson(mean_children_per_couple)
            checkToLimitAddToList(parent_occurrences, new_generation, parent1_idx, parent2_idx, num_children, founder_male, founder_female, limit_dic)     # Add offspring c>
        new_generation = random.sample(new_generation, pop_size)
        if generation==0:
            pop_sim_matrix[0]=new_generation
        else:
            pop_sim_matrix = np.vstack((pop_sim_matrix, new_generation))

    col_names = [f"i{i+1}" for i in range(pop_sim_matrix.shape[1])]
    row_names = [f"g{i+1}" for i in range(pop_sim_matrix.shape[0])]

    # Convert to a Pandas DataFrame
    df = pd.DataFrame(pop_sim_matrix, index=row_names, columns=col_names)
    df.to_csv("pedigree_{}f_{}m_{}g_mig{}_{}".format(female_number, male_number, num_generations,rep, migration_rate)  , sep='\t')
    return df


def getParents(dataframe, generation, individual_index):
    parents = dataframe.loc[f"g{generation}", f"i{individual_index}"].split("-")
    father_index, mother_index = map(int, parents)
    return father_index, mother_index

def traceBack(dataframe, current_generation, ancestors_by_generation_father, total_ind):
    ancestors_by_generation_father_new= []
    for i in (ancestors_by_generation_father): 
        parent1_index= i
        if parent1_index <= total_ind:
            father_lineage_parent1_index, father_lineage_parent2_index =getParents(dataframe, current_generation, parent1_index)
            ancestors_by_generation_father_new.append(father_lineage_parent1_index)
            ancestors_by_generation_father_new.append(father_lineage_parent2_index)
    ancestors_by_generation_father = ancestors_by_generation_father_new
    return ancestors_by_generation_father

def countLoops(ancestors_by_generation_father, ancestors_by_generation_mother):
    occurrences_dict = {}
    common_ancestors= set(ancestors_by_generation_mother) & set(ancestors_by_generation_father)
    for ancestor in common_ancestors:
        occurrences_in_mother = ancestors_by_generation_mother.count(ancestor)
        occurrences_in_father = ancestors_by_generation_father.count(ancestor)
        occurrences_dict[ancestor] = occurrences_in_mother * occurrences_in_father
    return occurrences_dict

def countNonUniqueElements(ancestors_by_generation_ca):
    count=Counter(ancestors_by_generation_ca)
    non_unique_dict = {item: count_item for item, count_item in count.items() if count_item > 1}
    return non_unique_dict

def findCommonAncestor(dataframe, generation, parent1_index, parent2_index, total_ind):

    #Start tracing back from the specified individual in the specified generation
    if generation < 1:
        return
    current_generation= generation-1

    ancestors_by_generation_father = getParents(dataframe, current_generation, parent1_index)
    ancestors_by_generation_mother = getParents(dataframe, current_generation, parent2_index)
    common_ancestors= set(ancestors_by_generation_mother) & set(ancestors_by_generation_father)
    ngen=2

    while len(common_ancestors) == 0  : #and current_generation < num_gens
        if(current_generation == 1):
            break 
        current_generation-=1
        # trace back for one generation
        ancestors_by_generation_father = traceBack(dataframe, current_generation, ancestors_by_generation_father, total_ind) 
        ancestors_by_generation_mother = traceBack(dataframe, current_generation, ancestors_by_generation_mother, total_ind)
        common_ancestors= set(ancestors_by_generation_mother) & set(ancestors_by_generation_father)

        ngen+=1

    occurrences_dict = countLoops(ancestors_by_generation_father, ancestors_by_generation_mother)
    return occurrences_dict, ngen, list(ancestors_by_generation_father), list(ancestors_by_generation_mother)


def calculate(simulated_data, generation, occurrences_dict, ngen, ancestors_by_generation_father, ancestors_by_generation_mother, total, ancestors_by_generation_ca, pooltype, num_gens, memo, total_ind):
    if generation < 0: 
        return total
    if(len(occurrences_dict))==0:
        return total
    
    for elem in occurrences_dict.keys():
        nloops = occurrences_dict[elem]
        nedges= 2*ngen            
        total += nloops* (((1/2)**(nedges-1))*(1+ calculateInbreedingCoefficient(simulated_data, generation-ngen, elem, num_gens, memo, total_ind)))
        if pooltype == PoolType.father_mother:
            if elem not in ancestors_by_generation_ca:
                ancestors_by_generation_ca.append(elem)
            while elem in ancestors_by_generation_father:
                ancestors_by_generation_father.remove(elem)
            while elem in ancestors_by_generation_mother:
                ancestors_by_generation_mother.remove(elem)
        elif pooltype == PoolType.father_ca:
            while elem in ancestors_by_generation_father:
                ancestors_by_generation_father.remove(elem)
        elif pooltype == PoolType.mother_ca:
            while elem in ancestors_by_generation_mother:
                ancestors_by_generation_mother.remove(elem)
    return total


def calculateInbreedingCoefficient(simulated_data, generation, individual_index, num_gens, memo, total_ind):
    max_attempt = 15
    if generation <= 1: 
        return 0

    if (generation, individual_index) in memo:
        return memo[(generation, individual_index)]
    
    if individual_index > total_ind:
        return 0

    father_index, mother_index = getParents(simulated_data, generation, individual_index)
    if father_index is None or father_index > total_ind or mother_index > total_ind: #ind from outside
        return 0
    
    occurrences_dict, ngen, ancestors_by_generation_father, ancestors_by_generation_mother =findCommonAncestor(simulated_data, generation, father_index, mother_index, total_ind)
    if(len(occurrences_dict))==0:
        return 0
    total=0
    ancestors_by_generation_ca = []
    for elem in occurrences_dict.keys():

        nloops = occurrences_dict[elem]
        nedges= 2*ngen
        ancestors_by_generation_ca.append(elem)
        total += nloops* (((1/2)**(nedges-1))*(1+ calculateInbreedingCoefficient(simulated_data, generation-ngen, elem, num_gens, memo, total_ind)))
        while elem in ancestors_by_generation_father:
            ancestors_by_generation_father.remove(elem)
        while elem in ancestors_by_generation_mother:
            ancestors_by_generation_mother.remove(elem)
    while (len(ancestors_by_generation_father)!=0 or len(ancestors_by_generation_mother)!=0) and generation-ngen > 0  and generation > num_gens - 15: 
        common_ancestors=[]
        attempts=0

        while len(common_ancestors) == 0 and attempts < max_attempt and generation-ngen >= num_gens-15:
            if(generation-ngen < 1):
                 break 
            # trace back for one generation

            ancestors_by_generation_father = traceBack(simulated_data, generation-ngen, ancestors_by_generation_father, total_ind) 
            ancestors_by_generation_mother = traceBack(simulated_data, generation-ngen, ancestors_by_generation_mother, total_ind)
            ancestors_by_generation_ca = traceBack(simulated_data, generation-ngen, ancestors_by_generation_ca, total_ind)
            common_ancestors = list(set(ancestors_by_generation_mother) & set(ancestors_by_generation_father))
            common_ancestors.extend(list(set(ancestors_by_generation_ca) & set(ancestors_by_generation_father)))
            common_ancestors.extend(list(set(ancestors_by_generation_ca) & set(ancestors_by_generation_mother)))

            ngen+=1
            attempts+=1

        if attempts >= max_attempt or generation-ngen == 0 :
            break
        if generation-ngen < num_gens- 15:
            break

        occurrences_dict_ca_within = countNonUniqueElements(ancestors_by_generation_ca)
        ancestors_by_generation_ca=list(set(ancestors_by_generation_ca))
        occurrences_dict_father_mother = countLoops(ancestors_by_generation_father, ancestors_by_generation_mother)
        occurrences_dict_ca_father = countLoops(ancestors_by_generation_ca, ancestors_by_generation_father)
        occurrences_dict_ca_mother = countLoops(ancestors_by_generation_ca, ancestors_by_generation_mother)


        total = calculate(simulated_data, generation, occurrences_dict_father_mother, ngen, ancestors_by_generation_father, ancestors_by_generation_mother, total, ancestors_by_generation_ca, PoolType.father_mother, num_gens, memo, total_ind)
        total = calculate(simulated_data, generation, occurrences_dict_ca_father, ngen, ancestors_by_generation_father, ancestors_by_generation_mother, total, ancestors_by_generation_ca, PoolType.father_ca, num_gens, memo, total_ind)
        total = calculate(simulated_data, generation, occurrences_dict_ca_mother, ngen, ancestors_by_generation_father, ancestors_by_generation_mother, total, ancestors_by_generation_ca, PoolType.mother_ca, num_gens, memo, total_ind)
        total = calculate(simulated_data, generation, occurrences_dict_ca_within, ngen, ancestors_by_generation_father, ancestors_by_generation_mother, total, ancestors_by_generation_ca, PoolType.within_ca, num_gens, memo, total_ind)

    memo[(generation, father_index, mother_index)] = total    
    return total


##main
def main(args):

    num_gens = args.num_gens
    female = args.female
    male = args.male
    rep_range= args.rep
    migration_rate = args.migration_rate
    max_child_mean= args.max_child_mean
    seed = 17
    mean_children_per_couple = args.mean_children_per_couple
    total_ind= female + male 

    for rep in range(1, int(rep_range)+1):
        memo = {}
        loss = []
        Fped_list = []
        simulated_data = simulatePopulation(male, female, num_gens, seed, mean_children_per_couple, max_child_mean, rep, migration_rate, memo)

        for i in range(1, total_ind+1):
            fped = calculateInbreedingCoefficient(simulated_data,num_gens, i, num_gens, memo, total_ind)
            Fped_list.append(fped)

        with open('female{}_male{}_gen{}_m{}_r{}.txt'.format(female, male, num_gens, migration_rate, rep), 'w') as f:
            for item in Fped_list:
                f.write(str(item) + '\n')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pedigre Simulation and Inbreeding Coefficient Calculation")
    parser.add_argument("female", type=int, help="female number")
    parser.add_argument("male", type=int, help="male number")
    parser.add_argument("num_gens",type= int, help="Number of generations")
    parser.add_argument("rep",type=str, help="replica number")
    parser.add_argument("migration_rate", type = float)
    parser.add_argument("--max_child_mean", type=int, default=7, help="Maximum mean number of children per couple (default: 7)")
    parser.add_argument("--mean_children_per_couple", type=int, default=2, help="Mean number of children per couple (default: 2)")
    args = parser.parse_args()

    main(args)
