import sys
def LDS(nums, i=0, prev=sys.maxsize):

    # Base case: nothing is remaining
    if i == len(nums):
        return 0

    # case 1: exclude the current element and process the
    # remaining elements
    excl = LDS(nums, i + 1, prev)

    # case 2: include the current element if it is smaller
    # than the previous element in LDS
    incl = 0
    if nums[i] < prev:
        incl = 1 + LDS(nums, i + 1, nums[i])

    # return the maximum of the above two choices
    return max(incl, excl)
