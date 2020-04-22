# Collecting object videos with Mepthisto

## Steps to collect a batch of videos using AMT:
1. Open `david_multihit.py` and edit two variables:
    - `classes_per_hit`
    - `hits_per_class`
2. run `python david_multihit.py` and wait for the AMT jobs to end.

## Then continue with running the automatic data checks:
3. CD to your clone of https://github.com/fairinternal/RoomViews/blob/master/object_dataset_collection/amt_data_check/
4. In `check_videos.py`, in `__main__` at the end of the file, edit `task_run_root` and `result_root` to your AMT collection directory and the directory which will contain the data-check results.
5. run `python check_videos.py`

_Note:_
- This requires MaskRCNN (included in the latest `torchvision`) and a compiled `AprilTag` QR code detector. 
- For now, we can simply skip the two aforementioned steps and only run the checks that validate the files are videos of a certain minimal duration.
- The latter can be done by simply commenting lines 147-171 in https://github.com/fairinternal/RoomViews/blob/master/object_dataset_collection/amt_data_check/check_videos.py

## Finally reward the workers based on the results of the previous data check:
5. CD back to `mephisto`
6. In `david_rewards.py` edit:
    - `task_run_id` (set to the id of the task run)
    - `data_check_root` - this is the root for the results of the data check script `check_videos.py`
7. run `python david_rewards.py`