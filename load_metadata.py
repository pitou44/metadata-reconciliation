# pip install pandas, openpyxl
import warnings
import pandas as pd
import math

from pandas.core.dtypes.inference import is_float

warnings.filterwarnings('ignore')


class Metadata:
    def __init__(self):
        files = ["ancient_art", "ancient_egypt", "architecture", "artists_2024", "asian_art", "manuscripts", "primitive"]
        self.data = {}

        print("--- Starting to load metadata ---")

        for file in files:
            df = pd.read_excel(f'metadata/{file}.xlsx')

            counts = df[df.columns[0]].value_counts()
            mask = df[df.columns[0]].duplicated(keep=False)
            # df.loc[mask, df.columns[0]] = df.loc[mask, df.columns[0]].astype(str) + '_' + \
            #                               df.groupby(df.columns[0]).cumcount()[mask].add(1).astype(str)

            df = df.drop_duplicates(subset=df.columns[0], keep='first')

            self.data = {**df.set_index(df.columns[0]).to_dict('index'), **self.data}

            del df

            print(f"FILE {file} loaded into memory")

        print("--- Metadata completely loaded ---")

    def print_values(self):
        tmp = 0
        for id in self.data.keys():
            print(id)
            # filter NaN to just regular None
            for tag in self.data[id].keys():
                if is_float(self.data[id][tag]):
                    if math.isnan(self.data[id][tag]):
                        self.data[id][tag] = None

            print(self.data[id])

            tmp += 1
            if tmp > 100:
                exit()

    def get_code_info(self, code):
        return f"{code} with the following metadata attached to it: {self.data[int(code)]}"
