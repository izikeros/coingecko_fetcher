from gecko_fetcher import get_coingecko_front_page


class TestGetCoingeckoFrontPage:
    def setup_class(self):
        # setup_class called once for the class"
        self.n_entries = 5
        self.pages = 3
        self.resp = get_coingecko_front_page(n=self.n_entries, p_max=self.pages)

    def test_get_coingecko_front_page__is_list(self):
        assert isinstance(self.resp, list), "response is not a list"

    def test_get_coingecko_front_page__list_not_empty(self):
        assert len(self.resp) > 0, "response is empty"

    def test_get_coingecko_front_page__list_len_correct(self):
        expected = self.n_entries * self.pages
        actual = len(self.resp)
        assert actual == expected, f"response has a wrong length {actual} instead of {expected}"

    def test_get_coingecko_front_page__list_element_is_dict(self):
        assert isinstance(self.resp[0], dict), "element of the list is not a dict"
