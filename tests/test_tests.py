from pytest import mark as m

@m.describe("When running tests")
@m.it("Should run them successfully")
def test_tests():
    assert True