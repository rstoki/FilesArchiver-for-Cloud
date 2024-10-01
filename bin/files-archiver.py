
import os
import sys
from os.path import basename

import click
import numpy as np
import pandas as pd
import shutil

THIS_FILE_PATH = __file__ if os.path.isabs(__file__) else os.path.join(os.getcwd(), __file__)
FILE_CONTAINING_FOLDER = os.path.dirname(THIS_FILE_PATH)
PROJECT_BASE_DIR = os.path.abspath(f'{FILE_CONTAINING_FOLDER}/..')
sys.path.append(PROJECT_BASE_DIR)
sys.path.append(f'{PROJECT_BASE_DIR}/src')

import rstoki_common.io_helpers as io_helpers


#%%

def get_parent_dirs(dirpath):
    chunks = dirpath.split(os.sep)
    result = []
    for i in range(len(chunks)):
        result.append(os.sep.join(chunks[0:i+1]))

    return result

def cum_sums_to_df(cumulative_sums_dict: dict[str, np.ndarray]) -> pd.DataFrame:

    records_for_df = []
    for key, val in cumulative_sums_dict.items():
        records_for_df.append(
            {
                'path': key,
                'NumFiles': val[0],
                'NumDirs': val[1]
            }
        )


    df = pd.DataFrame(records_for_df)
    return df


#%%
@click.group()
def cli():
    pass

#%%


@cli.command()
@click.option('-s', 'scan_dir', type=click.Path(exists=True, file_okay=False), help='Path to the root dir, where to start the scan.')
@click.option('-v', '--verbose', default=False, is_flag=True, help="Turn on verbose logging.")
@click.option('-n', '--test-only', default=False, is_flag=True, help="Test-only flag -- if set, the script will process only the first examination This flag is intended to be used only for development/debugging purposes.")
def scan(scan_dir, verbose, test_only):
    click.echo("Hello! This is THE command. ")

    cumulative_sums = {}

    saveto_path = f'report.xlsx'

    counter = 0
    for (dirpath, dirnames, filenames) in os.walk(scan_dir):
        counter += 1
        # click.echo(f'Dir: {dirpath}: {len(filenames)} files + {len(dirnames)} directories')

        num_files = len(filenames)
        num_dirs = len(dirnames)

        dir_basename = os.path.basename(dirpath)
        if dir_basename.startswith('.'):
            # -- if the directry is hidden (i.e., the name starts with a dot '.'), SKIP it
            continue

        all_subdirs = get_parent_dirs(dirpath)
        for subdir in all_subdirs:
            cs = cumulative_sums.get(subdir, np.zeros((2,)))
            cs += np.array([num_files, num_dirs])
            cumulative_sums[subdir] = cs

        if counter % 1000 == 0:
            click.echo(f'Processed {counter} dirs...')

        if counter % 10000 == 0:

            click.echo(f'Processed {counter} dirs...')



    records_for_df = []
    for key,val in cumulative_sums.items():
        records_for_df.append(
            {
                'path': key,
                'NumFiles': val[0],
                'NumDirs': val[1]
            }
        )
        pass

    df = pd.DataFrame(records_for_df)


    saveto_path = f'report.xlsx'
    df.to_excel(saveto_path, index=False)

    click.echo(f'Report saved as: {saveto_path}')


#%%

@cli.command()
@click.option('-s', 'src_dir', type=click.Path(exists=True, file_okay=False), help='Path to the root dir, where to start the scan.')
@click.option('-x', 'except_dir', multiple=True, default=None, help='Exclude this subdir. Specify only the name of dir. This parameter can be mentioned multiple times to exclude multiple dirs.')
@click.option('-d', 'process_dir', multiple=True, default=None, help='Archive only these explicitly mentioned subdirs. If at least one is specified, only mentioned dirs are processed.')
def archive_subdirs_individually(src_dir, except_dir, process_dir):

    # click.echo(f"param src_dir: {src_dir}")
    # click.echo(f"params: except_dir: {except_dir}")
    # click.echo(f"params: this_dir: {process_dir}")

    REMOVE_ME_PREFIX = '.OFF-REMOVE-ME'


    all_subdirs = io_helpers.list_subdirectories(src_dir)
    all_subdirs_set = set(all_subdirs)

    if (process_dir != None) and (len(process_dir) > 0):
        which_dirs_to_process_set = set(process_dir).intersection(all_subdirs_set)
    else:
        which_dirs_to_process_set = all_subdirs_set - set(except_dir)


    click.echo(f"Will process the following subdirs ({len(which_dirs_to_process_set)}):\n------------------- \n{which_dirs_to_process_set}\n-------------------")

    counter_done = 0
    for subdir in which_dirs_to_process_set:
        dirpath = os.path.join(src_dir, subdir)
        dst_zip_path = dirpath  # <-- just the BASE-name, because the shutil.make_archive() adds the extension '.zip' on its own!
        dst_zip_path_full = dst_zip_path + '.zip'

        if os.path.exists(dst_zip_path_full):
            click.secho(f'(EE) !!!  ERROR !!! ZIP archive {dst_zip_path_full} already exists, skipping...', fg='red')
            continue
        else:
            click.echo(f"Compressing folder:  {subdir} \t --> {dst_zip_path} .... ")
            try:
                shutil.make_archive(dst_zip_path, 'zip', dirpath)

                if os.path.exists(dst_zip_path_full):
                    counter_done += 1
                    subdir_name_OFF = f'{REMOVE_ME_PREFIX} {subdir}'
                    dirpath_after_rename = os.path.join(src_dir, subdir_name_OFF)
                    os.rename(dirpath, dirpath_after_rename)

                    pass
            except Exception as e:
                click.secho(f'(EE) !!!  Exception during compression: {e}. Skipping...', fg='red')

                if os.path.exists(dst_zip_path_full):
                    os.remove(dst_zip_path_full)    # <-- if Exception occured in the middle of `make_archive()` function, the 'stub' of ZIP file may already exists. We will remove it:
                pass
        pass

    pass

    click.secho(f"Finished {counter_done} archives!", fg="green")
    click.secho(f"Directories which have been archived were JUST RENAMED with '{REMOVE_ME_PREFIX}' prefix!!\nPlease go, check the ZIP archives, and REMOVE the old folders.", fg='blue', bg='white')


#%%


# > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > >
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > >

if __name__ == '__main__':
    cli()


