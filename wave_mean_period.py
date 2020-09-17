import numpy as np
from flask import  render_template

from flask import Flask
app = Flask(__name__)

@app.route('/plot')
def plot():
    #################################################################333333
    # Final plot.
    # High Significant

    from shapely.geometry import Point, Polygon
    import pandas as pd

    import numpy as np
    import geoviews as gv

    import bokeh

    import panel as pn

    import holoviews as hv
    from holoviews import opts
    from holoviews.operation.datashader import datashade, rasterize
    hv.extension("bokeh")

    import math

    from bokeh.models import HoverTool

    from scipy.interpolate import griddata
    from scipy.io import loadmat

    import datetime

    from dateutil.parser import parse

    from datetime import timedelta
    import time
    strtt = time.time()

    #datamat = loadmat('IOEC_ECM_noDA_20190703_masked.mat')
    datamat = loadmat('newtest_Tm02.mat')

    Xp = datamat['Xp']
    Yp = datamat['Yp']

    # Xp=np.where(((Xp>= 85) & (Xp<=88) & (Yp>=19) & (Yp<=22)),Xp,88)
    # Yp=np.where(((Xp>= 85) & (Xp<=88) & (Yp>=19) & (Yp<=22)),Yp,22)

    strt = datetime.datetime(2019, 7, 4, 0, 0)
    end = datetime.datetime(2019, 1, 13, 0, 0)
    from bokeh.models.callbacks import CustomJS

    def perdelta(strt, end, delta):
        curr = strt
        while curr < end:
            yield curr
            curr += delta

    # Read element file

    tri_new = pd.read_csv('fort.ele', delim_whitespace=True, names=('A', 'B', 'C', 'D'), usecols=[1, 2, 3], skiprows=1,
                          dtype={'D': np.int})

    dateList = []



    def plotthis(datetime, regions='Whole_East_Coast'):
        dat = datetime
        # datetostr=result.strftime("%Y%b%d%H")
        dt = parse(str(dat))
        yr = dt.year
        mn = dt.month
        d = dt.day
        hr = dt.hour
        mi = dt.minute

        if hr < 10:

            hr = '0' + str(hr)
        else:
            d = str(d)
            hr = str(hr)
        if int(d) < 10:
            d = '0' + str(d)
        else:
            d = str(d)
        varname = 'Tm02_' + str(yr) + '0' + str(mn) + str(d) + '_' + hr + '0000'

        x = Xp.flatten()
        y = Yp.flatten()
        z = datamat[varname]

        if regions is 'Odisha':
            z = np.where(((Xp >= 85) & (Xp <= 88) & (Yp >= 19) & (Yp <= 22)), z, np.nan).flatten()
        elif regions is 'Andra_Pradesh':
            z = np.where(((Xp >= 79) & (Xp <= 85) & (Yp >= 13) & (Yp <= 19)), z, np.nan).flatten()
        elif regions is 'Tamil_Nadu':
            z = np.where(((Xp >= 77) & (Xp <= 83) & (Yp >= 7) & (Yp <= 14)), z, np.nan).flatten()
        elif regions is 'Whole_East_Coast':
            z = z.flatten()

        else:
            #         data = get_data4region(data,**odisha)
            z = z.flatten()

        # z = z.flatten()
        Longitude = x
        Latitude = y
        MeanWavePeriod = z

        pts = np.stack((Longitude, Latitude, MeanWavePeriod)).T
        verts = pd.DataFrame(np.stack((Longitude, Latitude, MeanWavePeriod)).T,
                             columns=['Longitude', 'Latitude', ' MeanWavePeriod'])

        # openStreet Background.
        tri_sub = tri_new.apply(lambda x: x - 1)
        ggpoints = gv.Points(verts, vdims=[' MeanWavePeriod'])
        ggsubraster = rasterize(gv.TriMesh((tri_sub, gv.Points(verts))))

        tri = gv.TriMesh((tri_sub, gv.Points(verts)))

        return tri

    allplot = {(k.strftime("%Y-%m-%d %H:%M:%S"), r): plotthis(k, r) for k in
               perdelta(strt, strt + timedelta(days=2), timedelta(hours=18)) for r in
               ['Odisha', 'Andra_Pradesh', 'Whole_East_Coast', 'Tamil_Nadu']}


    df_div = hv.Div("""
        <figure>
        <img src="https://i.ibb.co/S0t5GWb/imglogo.png" height='80' width='90' vspace='-10'>
        """)

    df_div1 = hv.Div("""
        &nbsp<center><b><p style="color:#B22222";font-size:80px;font-family:Times new roman><h1 style=font-size:20px;margin-left:2.5em;margin-top:-1em;color:#B22222>Indian National Center for Ocean Information Services<br />
        (INCOIS)</h1></p></b></center>

        """)

    colorbar_opts = {
        'major_label_overrides': {
            0: '0',

            1: '1',

            2: '2',

            3: '3',

            4: '4',

            5: '5',
            6: '6',

            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: '11',
            12: '12',
            13: '13',
            14: '>14',
            15: '15'

        },
        'major_label_text_align': 'left', 'major_label_text_font_style': 'bold', }
    levels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, ]
    def disable_logo(plot, element):
        plot.state.toolbar.logo = None

    hv.plotting.bokeh.ElementPlot.finalize_hooks.append(disable_logo)

    # logo1 = hv.RGB.load_image("imglogo.png")

    logo1 = hv.RGB.load_image("https://i.ibb.co/7VXRPCS/logo1.png")

    def absolute_position(plot, element):
        glyph = plot.handles['glyph']
        x_range, y_range = plot.handles['x_range'], plot.handles['y_range']
        glyph.dh_units = 'screen'
        glyph.dw_units = 'screen'
        glyph.dh = 60
        glyph.dw = 90
        glyph.x = x_range.start
        glyph.y = y_range.start
        xcode = CustomJS(code="glyph.x = cb_obj.start", args={'glyph': glyph})
        plot.handles['x_range'].js_on_change('start', xcode)
        ycode = CustomJS(code="glyph.y = cb_obj.start", args={'glyph': glyph})
        plot.handles['y_range'].js_on_change('start', ycode)

    def plot_limits(plot, element):
        plot.handles['x_range'].min_interval = 100
        plot.handles['x_range'].max_interval = 55000000
        # 3000000
        plot.handles['y_range'].min_interval = 500
        plot.handles['y_range'].max_interval = 900000

    opts = dict(width=700, height=700, tools=['hover', 'save', 'wheel_zoom'], active_tools=['wheel_zoom'],
                hooks=[plot_limits, disable_logo], colorbar=True, color_levels=15,
                colorbar_opts=colorbar_opts, cmap=['#000080',
                                                   '#0000cd',

                                                   '#0008ff',
                                                   '#004cff',
                                                   '#0090ff',
                                                   '#00d4ff',
                                                   '#29ffce',
                                                   '#60ff97',
                                                   '#97ff60',
                                                   '#ceff29',
                                                   '#ffe600',
                                                   '#ffa700',
                                                   # '#ff6800',
                                                   '#ff2900',
                                                   '#cd0000',
                                                   '#800000',

                                                   ], clim=(0, 15), title="\t\t\t\t\t\t\t\t\t Mean Wave Period (s) ",
                fontsize={'title': 18, 'xlabel': 15, 'ylabel': 15, 'ticks': 12})

    tiles = gv.tile_sources.Wikipedia
    hmap1 = hv.HoloMap(allplot, kdims=['Select Date and Time :', 'Select Indian State'])


    dd = df_div.opts(width=70, height=70)
    dd1 = df_div1.opts(width=600, height=90)

    finalplot = pn.Column(pn.Row(dd, dd1),
                          tiles * rasterize(hmap1).options(**opts) * logo1.opts(hooks=[absolute_position],
                                                                                        apply_ranges=False))
    print("types of finalplot:",type(finalplot))
    print("finalplot:",finalplot)
    # print("--- %s seconds ---" % (time.time() - strtt))
    from bokeh.embed import components
    from bokeh.resources import CDN
    from bokeh.io import curdoc
    doc = curdoc()
    script, div = components(finalplot.get_root(doc))
    cdn_js0=CDN.js_files[0]
    cdn_js = CDN.js_files[1]
    cdn_css=CDN.css_files
    print("cdn_js:",cdn_js)
    print("cdn_css",cdn_css)

    return render_template("plot.html",
                           script=script,
                           div=div,
                           cdn_css=cdn_css,
                           cdn_js=cdn_js,
                           cdn_js0=cdn_js0)


# @app.route('/')
# def home():
#     return render_template("home.html")
#
#
# @app.route('/about/')
# def about():
#     return render_template("about.html")



if __name__=='__main__':
    app.run(debug=True)