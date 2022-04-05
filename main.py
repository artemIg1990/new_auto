
import asyncio
import datetime
from collections import Counter

from grapi import Grapi

from cred import token
from test_cases import cases


def find_update_message(messages):
    log_entry = "Upload completed successfully. Reboot ..."

    for i in range(len(messages)):
        if log_entry == messages[i]["message"]["message"]:
            return i
    return None


async def main():
    # Initialize Grapi
    url = "https://graylog.omnic.solutions/api/search/universal/absolute"
    my_api = Grapi(url, token)

    # Get user input
    date_from_input = input("Enter date from (DD.MM.YY HH:MM): ")
    date_to_input = input("Enter date to (DD.MM.YY HH:MM): ")
    postomat_from_input = input("Enter postomat from: ")
    postomat_to_input = input("Enter postomat to: ")
    print("\n")

    # Parse input
    datetime_from = None
    datetime_to = None
    postomat_range_from = None
    postomat_range_to = None
    try:
        datetime_from = datetime.datetime.strptime(date_from_input, '%d.%m.%y %H:%M')
        datetime_to = datetime.datetime.strptime(date_to_input, '%d.%m.%y %H:%M')
        postomat_range_from = int(postomat_from_input)
        postomat_range_to = int(postomat_to_input)
    except ValueError:
        print("Wrong date or postomat format")
        exit(2)

    # Convert datetime to graylog API format
    datetime_from_string = datetime_from.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    datetime_to_string = datetime_to.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Run test cases for each postomat
    total_result = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    for postomat_num in range(postomat_range_from, postomat_range_to):

        limit = 10000  # max limit for graylog
        my_params = {
            "query": f"source:{postomat_num}",  # Required
            "fields": ["message, source"],  # Required
            "filter": "streams:000000000000000000000001",
            "from": datetime_from_string,  # Required
            "to": datetime_to_string,  # Required
            "limit": limit,  # Optional: Default limit is 150 in Graylog
            "sort": "timestamp:asc"
        }
        res = my_api.send("get", **my_params)
        res = res.json()  # Convert response json to dict

        # Chunk splitting is not implemented yet
        if res["total_results"] > limit:
            print(f"Too many results for postomat {postomat_num} Tests may be inaccurate...")

        case_results = [None] * len(cases)

        update_message_idx = find_update_message(res["messages"])
        if update_message_idx is None:
            print(f"No update message found for postomat {postomat_num}")

        # Run test cases
        for case in cases:
            case_num = cases.index(case)
            if case.test is not None:
                case_result = case.test(res["messages"], update_message_idx)
            else:
                case_result = None

            case_results[case_num] = case_result
            if case_result is True:
                print(f"Case {case_num + 1} \"{case.name}\" passed!")
            elif case_result is False:
                print(f"* Case {case_num + 1} \"{case.name}\" failed!")
            else:
                print(f"* Case {case_num + 1} \"{case.name}\" skipped!")

        # Count results and add to total
        case_results_dict: dict[bool or None, int] = dict(Counter(case_results))
        case_results_dict.setdefault(True, 0)
        case_results_dict.setdefault(False, 0)
        case_results_dict.setdefault(None, 0)

        total_result["passed"] += case_results_dict[True]
        total_result["failed"] += case_results_dict[False]
        total_result["skipped"] += case_results_dict[None]
        total_result["total"] += len(case_results)

        print(f'Postomat: {postomat_num} Cases: {len(cases)} '
              f'Passed: {case_results_dict[True]} '
              f'Failed: {case_results_dict[False]} '
              f'Skipped: {case_results_dict[None]} '
              f'Percentage: {(case_results_dict[True] + case_results_dict[None]) / len(cases) * 100}%'
              f'\n')

    # Print total results
    print()
    percentage = (total_result["passed"] + total_result["skipped"]) / total_result["total"] * 100
    print(f'Total Cases: {total_result["total"]} \n'
          f'Passed: {total_result["passed"]} \n'
          f'Failed: {total_result["failed"]} \n'
          f'Skipped: {total_result["skipped"]} \n'
          f'Percentage: {percentage}% \n')

    if percentage == 100:
        print("All tests passed!")
        exit(0)
    else:
        print("Some tests failed!")
        exit(1)


# Run main function
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
