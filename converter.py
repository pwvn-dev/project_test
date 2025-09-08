# converter.py
from converters_tab_1.zeiss_AFP import ZeissConverter as ZeissConverterTab1
from converters_tab_1.mitutoyo_AFP import MitutoyoConverter as MitutoyoConverterTab1
from converters_tab_1.mahr_AFP import MahrConverter as MahrConverterTab1

from converters_tab_2.zeiss_pwi import ZeissConverter as ZeissConverterTab2
from converters_tab_2.mitutoyo_pwi import MitutoyoConverter as MitutoyoConverterTab2
from converters_tab_2.mahr_pwi import MahrConverter as MahrConverterTab2

# Bạn có thể mở rộng, thêm map hay helper ở đây

def get_converter(tab, brand, root_data, afp_to_dl, log_dir):
    """
    Trả về instance converter phù hợp với tab và brand,
    tab: 'tab1' hoặc 'tab2'
    brand: 'Zeiss', 'Mitutoyo', 'Mahr'
    """
    if tab == 'tab1':
        map_tab1 = {
            'Zeiss': ZeissConverterTab1,
            'Mitutoyo': MitutoyoConverterTab1,
            'Mahr': MahrConverterTab1,
        }
        ConverterCls = map_tab1.get(brand)
    elif tab == 'tab2':
        map_tab2 = {
            'Zeiss': ZeissConverterTab2,
            'Mitutoyo': MitutoyoConverterTab2,
            'Mahr': MahrConverterTab2,
        }
        ConverterCls = map_tab2.get(brand)
    else:
        ConverterCls = None

    if ConverterCls is None:
        raise ValueError(f"No converter for tab={tab}, brand={brand}")

    return ConverterCls(root_data, afp_to_dl, log_dir)
