# Copyright (c) 2021 The AlasKA Developers.
# Distributed under the terms of the MIT License.
# SPDX-License_Identifier: MIT
"""
contains the keyword tree extractor and alias class
"""
import os.path
import gzip
import json
import logging

import pandas as pd
import seaborn as sns
import lasio

# alaska imports
from .predict_from_model import make_prediction
from .get_data_path import get_data_path

sns.set()


class Node:
    """
    Node class for use in the keyword tree extractor
    """

    def __init__(self, key):
        self.key = key
        self.child = []


def make_tree():
    """
    :param: None
    :return: m-ary tree of keywords that forms keyword extractor tree
    Generates keyword extractor tree
    """

    original_lowered_csv = get_data_path("original_lowered.csv")

    root = Node(None)
    df = pd.read_csv(original_lowered_csv).drop("Unnamed: 0", 1).reset_index(drop=True)
    arr = df.label.unique()
    cali_arr = ["calibration", "diameter", "radius"]
    time_arr = ["time", "delta-t", "dt", "delta"]
    gr_arr = ["gamma", "ray", "gr", "gamma-ray"]
    sp_arr = ["sp", "spontaneous", "potential"]
    d_arr = ["correction", "porosity"]
    p_arr = ["density", "neutron", "sonic"]
    p2_arr = ["dolomite", "limestone"]
    r_arr = ["deep", "shallow", "medium"]
    sr_arr = ["a10", "a20", "ae10", "ae20", "10in", "20in"]
    mr_arr = ["a30", "ae30", "30in"]
    dr_arr = ["a60", "a90", "ae60", "ae90", "60in", "90in"]
    j = 0
    for i in arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node(i))
        j += 1
    for i in cali_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("caliper"))
        j += 1
    for i in time_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("sonic travel time"))
        j += 1
    for i in gr_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("gamma ray"))
        j += 1
    for i in sp_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("spontaneous potential"))
        j += 1
    root.child.append(Node("photoelectric"))
    root.child[j].child.append(Node("photoelectric effect"))
    j += 1
    root.child.append(Node("bit"))
    root.child[j].child.append(Node("bit size"))
    j += 1
    for i in sr_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("shallow resistivity"))
        j += 1
    for i in mr_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("medium resistivity"))
        j += 1
    for i in dr_arr:
        root.child.append(Node(i))
        root.child[j].child.append(Node("deep resistivity"))
        j += 1
    root.child.append(Node("density"))
    k = 0
    for i in d_arr:
        root.child[j].child.append(Node(i))
        st = "density " + str(i)
        root.child[j].child[k].child.append(Node(st))
        k += 1
    root.child[j].child.append(Node("bulk"))
    root.child[j].child[k].child.append(Node("bulk density"))
    root.child.append(Node("porosity"))
    j += 1
    k = 0
    for i in p_arr:
        root.child[j].child.append(Node(i))
        st = str(i) + " porosity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    for i in p2_arr:
        root.child[j].child.append(Node(i))
        st = "density porosity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    root.child.append(Node("conductivity"))
    j += 1
    k = 0
    for i in r_arr:
        root.child[j].child.append(Node(i))
        st = str(i) + " conductivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    root.child.append(Node("resistivity"))
    j += 1
    k = 0
    for i in r_arr:
        root.child[j].child.append(Node(i))
        st = str(i) + " resistivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    for i in sr_arr:
        root.child[j].child.append(Node(i))
        st = "shallow resistivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    for i in mr_arr:
        root.child[j].child.append(Node(i))
        st = "medium resistivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    for i in dr_arr:
        root.child[j].child.append(Node(i))
        st = "deep resistivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    root.child[j].child.append(Node("micro"))
    st = "micro resistivity"
    root.child[j].child[k].child.append(Node(st))
    root.child.append(Node("res"))
    j += 1
    k = 0
    for i in r_arr:
        root.child[j].child.append(Node(i))
        st = str(i) + " resistivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    root.child.append(Node("cond"))
    j += 1
    k = 0
    for i in r_arr:
        root.child[j].child.append(Node(i))
        st = str(i) + " conductivity"
        root.child[j].child[k].child.append(Node(st))
        k += 1
    return root


def search(tree, description):
    """
    :param tree: m-ary keyword extractor tree
    :param description: mnemonic description from LAS file
    :return: none if keyword does not exist in tree, label if keyword exists in tree
    Search keyword extractor tree
    """
    arr = [tree]
    arr = [c for node in arr for c in node.child if c]
    for i in description.split():
        for node in arr:
            if i == node.key:
                return search_child(node, description)
    return None


def search_child(node, description):
    """
    :param node: node of m-ary keyword extractor tree
    :param description: mnemonic description from LAS file
    :return: none if keyword does not exist in tree, label if keyword exists in tree
    Search keyword extractor node
    """
    if len(node.child) < 1:
        return None
    elif len(node.child) == 1:
        return node.child[0].key
    else:
        for i in description.split():
            for child in node.child:
                if i == child.key:
                    return search_child(child, description)
    return None


class Alias:
    """
    :param dictionary: boolean for dictionary aliasing
    :param custom_dict: string path to a custom dictionary in either .json or .csv
    :param keyword_extractor: boolean for keyword extractor aliasing
    :param model: boolean for model aliasing
    :param prob_cutoff: probability cutoff for pointer generator model
    :return: dictionary of mnemonics and labels, list of mnemonics not aliased
    Parses LAS file and returns parsed mnemonics with labels
    """

    # Constructor
    def __init__(
        self,
        dictionary=True,
        custom_dict=None,
        keyword_extractor=True,
        model=False,
        prob_cutoff=0.5,
    ):
        self.dictionary = dictionary
        self.custom_dict = custom_dict
        self.keyword_extractor = keyword_extractor
        self.prob_cutoff = prob_cutoff
        self.model = model
        self.duplicate, self.not_found = [], []
        self.method, self.probability, self.mnem = [], [], []
        self.output, self.formatted_output = {}, {}

    def parse(self, path):
        """
        :param path: path to LAS file to be aliased
        :return: dictionary of mnemonics and labels, list of mnemonics not aliased
        Parses LAS file and call parsers accordingly
        """
        las = lasio.read(path)
        mnem, desc = [], []
        for key in las.keys():
            mnem.append(key.lower())
            if str(las.curves[key].descr) == "" and str(las.curves[key].value) == "":
                desc.append("None")
            else:
                desc.append(str(las.curves[key].descr).lower())
        print("Reading {} mnemonics...".format(len(mnem)))
        if self.dictionary is True:
            self.dictionary_parse(mnem)
        if self.keyword_extractor is True:
            self.keyword_parse(mnem, desc)
        if self.model is True:
            df = self.make_df(path)
            self.model_parse(df)
        for key, val in self.output.items():
            self.formatted_output.setdefault(val, []).append(key.upper())
        return self.formatted_output, self.not_found

    def parse_directory(self, directory):
        """
        :param path: path to directory containing LAS files
        :return: dictionary of mnemonics and labels, list of mnemonics not aliased
        Parses LAS files and call parsers accordingly
        """
        comprehensive_dict = {}
        comprehensive_not_found = []
        for filename in os.listdir(directory):
            if filename.endswith((".LAS", ".las")):
                path = os.path.join(directory, filename)
                try:
                    las = lasio.read(path)
                except:
                    logging.warning(f"lasio was not able to read {filename}")
                    continue
                las = lasio.read(path)
                mnem, desc = [], []
                for key in las.keys():
                    mnem.append(key.lower())
                    if (
                        str(las.curves[key].descr) == ""
                        and str(las.curves[key].value) == ""
                    ):
                        desc.append("None")
                    else:
                        desc.append(str(las.curves[key].descr).lower())
                print("Reading {} mnemonics from {}...".format(len(mnem), filename))
                if self.dictionary is True:
                    self.dictionary_parse(mnem)
                if self.keyword_extractor is True:
                    self.keyword_parse(mnem, desc)
                if self.model is True:
                    df = self.make_df(path)
                    self.model_parse(df)
                comprehensive_dict.update(self.output)
                comprehensive_not_found.extend(self.not_found)
                self.output = {}
                self.duplicate, self.not_found = [], []
        for key, val in comprehensive_dict.items():
            self.formatted_output.setdefault(val, []).append(key.upper())
        return self.formatted_output, comprehensive_not_found

    def heatmap(self):
        """
        Plots a heatmap with mnemonics and prediction probabilities
        """
        df = pd.DataFrame(
            {"method": self.method, "mnem": self.mnem, "prob": self.probability}
        )
        result = df.pivot(index="method", columns="mnem", values="prob")
        fig = sns.heatmap(result)
        return fig

    def _dict_to_table(self, dicts):
        """
        :param dicts: python dictionary
        Converts a dictionary to mnemonic lookup table for dictionary parsing
        """
        dictlist = []
        for key, value in dicts.items():
            for item in value:
                dictlist.append([item, key])
        lookup_table = pd.DataFrame(dictlist, columns=["mnemonics", "label"])
        return lookup_table

    def _file_type_check(self, file_path):
        """
        :param file_path: string filepath to dictionary either .json or .csv
        Checks file path converts json to lookup table, passes .csv to dictionary_parse
        """
        if os.path.isfile(file_path) and file_path.endswith(".json"):
            with open(file_path) as json_file:
                dictionary = json.load(json_file)
            comprehensive_dictionary = self._dict_to_table(dicts=dictionary)
        elif os.path.isfile(file_path) and file_path.endswith(".csv"):
            comprehensive_dictionary = self.custom_dict
        elif (
            os.path.isfile(file_path)
            and not file_path.endswith(".json")
            or file_path.endswith(".csv")
        ):
            raise IOError(
                "Please check your dictionary type. AlasKA only accepts json and csv"
            )
        if isinstance(comprehensive_dictionary, pd.DataFrame):
            lookup_df = comprehensive_dictionary
        elif isinstance(comprehensive_dictionary, str):
            lookup_df = pd.read_csv(comprehensive_dictionary)
        return lookup_df

    def dictionary_parse(self, mnem):
        """
        :param mnem: list of mnemonics
        :return: None
        Find exact matches of mnemonics in mnemonic dictionary
        """
        if self.custom_dict is None:
            comprehensive_dictionary_csv = get_data_path("comprehensive_dictionary.csv")
            df = pd.read_csv(comprehensive_dictionary_csv)
        else:
            df = self._file_type_check(self.custom_dict)
        if not isinstance(df, pd.DataFrame):
            return ValueError(
                "The dictionary dataframe is empty, please check your custom dictionary"
            )
        print("Alasing with dictionary...")
        dic = df.apply(lambda x: x.astype(str).str.lower())
        aliased = 0
        for index, word in enumerate(mnem):
            if word in dic.mnemonics.unique():
                # can be reduced?
                key = dic.loc[dic["mnemonics"] == word, "label"].iloc[0]
                self.output[word] = key
                self.duplicate.append(index)
                self.mnem.append(word)
                self.probability.append(1)
                self.method.append("dictionary")
                aliased += 1
            else:
                self.not_found.append(word)
        print("Aliased {} mnemonics with dictionary".format(aliased))

    def keyword_parse(self, mnem, desc):
        """
        :param mnem: list of mnemonics
        :param desc: list of descriptions
        :return: None
        Find exact labels of mnemonics with descriptions that can be
        filtered through keyword extractor tree
        """
        Tree = make_tree()
        new_desc = [v for i, v in enumerate(desc) if i not in self.duplicate]
        new_mnem = [v for i, v in enumerate(mnem) if i not in self.duplicate]
        aliased = 0
        print("Alasing with keyword extractor...")
        for index, word in enumerate(new_desc):
            key = search(Tree, word)
            if key is None:
                if new_mnem[index] not in self.not_found:
                    self.not_found.append(new_mnem[index])
            else:
                self.output[new_mnem[index]] = key
                self.mnem.append(new_mnem[index])
                self.probability.append(1)
                self.method.append("keyword")
                if new_mnem[index] in self.not_found:
                    self.not_found.remove(new_mnem[index])
                aliased += 1
        print("Aliased {} mnemonics with keyword extractor".format(aliased))

    def model_parse(self, df):
        """
        :param df: dataframe of curves
        :return: None
        Make predictions using pointer generator
        """
        print("Alasing with pointer generator...")
        path = self.build_test(df)
        new_dictionary, predicted_prob = make_prediction(path)
        for key, value in predicted_prob.items():
            if float(value) >= self.prob_cutoff:
                self.output[key] = new_dictionary[key]
                self.mnem.append(key)
                self.probability.append(float(value))
                self.method.append("model")
                if key in self.not_found:
                    self.not_found.remove(key)
            else:
                self.not_found.append(key)
        print("Aliased {} mnemonics with pointer generator".format(len(predicted_prob)))

    def build_test(self, df):
        """
        :param df: dataframe of curves
        :return: compressed file of summaries used to generate labels
        Build input file for pointer generator
        """
        data_path = get_data_path("input.gz")
        test_out = gzip.open(data_path, "wt", encoding="utf-8")
        for i in range(len(df)):
            fout = test_out
            lst = [df.description[i], df.units[i], df.mnemonics[i]]
            summary = [df.mnemonics[i]]
            fout.write(" ".join(lst) + "\t" + " ".join(summary) + "\n")
            fout.flush()
        test_out.close()
        return str(data_path)

    def make_df(self, path):
        """
        :param path: path to the LAS file
        :return: dataframe of curves
        Build dataframe for pointer generator
        """
        mnem, description, unit = [], [], []
        las = lasio.read(path)
        if self.dictionary is not True and self.keyword_extractor is not True:
            for key in las.keys():
                mnem.append(key.lower())
                description.append(str(las.curves[key].descr).lower())
                unit.append(str(las.curves[key].unit).lower())
        else:
            for i in self.not_found:
                mnem.append(i)
                description.append(str(las.curves[i].descr).lower())
                unit.append(str(las.curves[i].unit).lower())
        output_df = pd.DataFrame(
            {"mnemonics": mnem, "description": description, "units": unit}
        )
        return output_df

    def add_to_dictionary(self, path=None):
        """
        Adds new aliases from model and keyword extractor to comprehensive dictionary. 
        By default it will overwrite the comprehensive dictionary
        :param path: path to save custom dictionary, default appends comprehensive
        """
        if not self.formatted_output:
            raise ValueError("The alias dictionary is empty. Please parse a LAS file")
        new_aliases = self._dict_to_table(dicts=self.formatted_output)
        comprehensive_dictionary_csv = pd.read_csv(
            get_data_path("comprehensive_dictionary.csv")
        )
        not_in_comprehensive = new_aliases[
            ~new_aliases["mnemonics"].isin(comprehensive_dictionary_csv["mnemonics"])
        ]
        munge_df = not_in_comprehensive.copy().drop("label", axis=1)
        munge_df["label"] = not_in_comprehensive["label"].str.upper()
        appended_df = comprehensive_dictionary_csv.append(
            munge_df, ignore_index=True, verify_integrity=True
        )
        if not path:
            appended_df.to_csv(
                get_data_path("comprehensive_dictionary.csv"),
                index=False,
                columns=["mnemonics", "label"],
            )
        else:
            if not path.endswith(".csv"):
                raise IOError(
                    "Please check your file name type. Custom paths must end with .csv"
                )
            else:
                appended_df.to_csv(path, index=False, columns=["mnemonics", "label"])
