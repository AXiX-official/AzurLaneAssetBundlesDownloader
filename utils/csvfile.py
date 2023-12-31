import pandas as pd


def merge_csv_with_conflicts(file1, file2, output_path=None, flag='merge'):
    """
    合并两个csv文件，如果有冲突则返回冲突的内容
    """
    names = ['file_name', 'size', 'md5']

    df1 = pd.read_csv(file1, header=None, names=names)
    df2 = pd.read_csv(file2, header=None, names=names)

    df = pd.merge(df1, df2, on='file_name', how='outer', suffixes=('_file1', '_file2'))

    # 找出size或者MD5不一致的
    conflicts = df[(df['size_file1'] != df['size_file2']) | (df['md5_file1'] != df['md5_file2'])]

    if flag == 'difference':
        return conflicts

    if flag == 'right':
        conflicts = conflicts.drop(['size_file1', 'md5_file1'], axis=1)
        conflicts = conflicts.dropna(axis=0, how='any')
        return conflicts

    if flag == 'merge':
        # 如果有值是空的则舍弃
        conflicts = conflicts.dropna(axis=0, how='any')

        # 把df中的conflicts的行去掉
        df = df.drop(conflicts.index)

        df['size'] = df['size_file1'].fillna(df['size_file2'])
        df['md5'] = df['md5_file1'].fillna(df['md5_file2'])
        df = df.drop(['size_file1', 'md5_file1', 'size_file2', 'md5_file2'], axis=1)

        # 保存时不带列名
        df.to_csv(output_path, index=False, header=False)

        return conflicts
