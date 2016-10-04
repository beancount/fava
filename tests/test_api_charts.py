def test_linechart_data(example_api):
    data = example_api.charts.linechart('Assets:Testing:MultipleCommodities')
    assert data[1]['balance']['USD'] == 50
    assert data[2]['balance']['USD'] == 0
