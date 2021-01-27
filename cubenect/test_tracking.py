import cubenect
import multitouch_driver_mock as mock_mtd

mock_driver = mock_mtd.MultitouchDriverMock()

cube = cubenect.Cubenect(debug=True)
cube.run(contact_update_callback=mock_driver.print_action_callback)
