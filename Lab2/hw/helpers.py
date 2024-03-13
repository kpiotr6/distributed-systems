from tabulate import tabulate


def build_response(data_list: [dict, dict], name1: str, name2: str, city: str):
    data_diffs = {}
    for k in data_list[0]:
        fd = data_list[0].get(k)
        sd = data_list[1].get(k)
        if isinstance(fd[0], str):
            data_diffs.update({k: fd})
        else:
            n_tab = []
            for i in range(len(fd)):
                n_tab.append(abs(fd[i] - sd[i]))
            data_diffs.update({k: n_tab})

    return f"""
        City Name: {city}<br>
        {name1}<br>
        {tabulate(data_list[0], headers="keys", tablefmt="html")}<br>
        {name2}<br>
        {tabulate(data_list[1], headers="keys", tablefmt="html")}<br>
        Absolute difference<br>
        {tabulate(data_diffs, headers="keys", tablefmt="html")}<br>
        """
