class TrackerMetrics:
    Email: int = 0
    EmailAggressive: int = 0
    Advertising: int = 0
    Content: int = 0
    Analytics: int = 0
    FingerprintingInvasive: int = 0
    FingerprintingGeneral: int = 0
    Social: int = 0
    Cryptomining: int = 0
    Disconnect: int = 0

    def reset(self):
        self.Email = 0
        self.EmailAggressive = 0
        self.Advertising = 0
        self.Content = 0
        self.Analytics = 0
        self.FingerprintingInvasive = 0
        self.FingerprintingGeneral = 0
        self.Social = 0
        self.Cryptomining = 0
        self.Disconnect = 0

# loop through the json file to find the purpose of the tracker
metrics = TrackerMetrics()
metrics.reset()
for tracker in input_data['hosts']["requests"]["third_party"]:
    found_category = None
    for category, entries in json_data['categories'].items():
        for entry in entries:
            for value_dict in entry.values():
                for url, values in value_dict.items():
                    url = url.replace("https://", "").replace("http://", "")
                    similarity_ratio = fuzz.ratio(tracker, url)
                    if similarity_ratio > 75:
                        print(tracker)
                        print(url)
                        print(category)
                        found_category = category
                        break
                    else:
                        for value in values:
                            similarity_ratio = fuzz.ratio(tracker, value)
                            if similarity_ratio > 75:
                                print(tracker)
                                print(url)
                                print(category)
                                found_category = category
                                break
                    if found_category:
                        break
                if found_category:
                    break
            if found_category:
                break
        if found_category:
            current_count = getattr(metrics, category)
            setattr(
                metrics,
                category,
                current_count + 1,
            )
            break