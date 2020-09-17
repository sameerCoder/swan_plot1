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

    datamat = loadmat('IOEC_ECM_noDA_20190703_masked.mat')
    # datamat = loadmat('IOEC_ECM_DA_20191121_masked.mat')

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
        varname = 'Steepn_' + str(yr) + '0' + str(mn) + str(d) + '_' + hr + '0000'

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
        HS = z

        pts = np.stack((Longitude, Latitude, HS)).T
        verts = pd.DataFrame(np.stack((Longitude, Latitude, HS)).T, columns=['Longitude', 'Latitude', 'HS'])

        # openStreet Background.
        tri_sub = tri_new.apply(lambda x: x - 1)
        ggpoints = gv.Points(verts, vdims=['HS'])
        ggsubraster = rasterize(gv.TriMesh((tri_sub, gv.Points(verts))))

        tri = gv.TriMesh((tri_sub, gv.Points(verts)))

        return tri

    allplot = {(k.strftime("%Y-%m-%d %H:%M:%S"), r): plotthis(k, r) for k in
               perdelta(strt, strt + timedelta(days=9), timedelta(hours=3)) for r in
               ['Odisha', 'Andra_Pradesh', 'Whole_East_Coast', 'Tamil_Nadu']}
    # allplot2={(k.strftime("%Y-%m-%d %H:%M:%S"),r):plotsecond(k,r)for k in perdelta(strt, strt + timedelta(days=1), timedelta(hours=18)) for r in ['Odisha','Andra_Pradesh','Whole_East_Coast','Tamil_Nadu']}

    df_div = hv.Div("""
        <figure>
        <img src="https://i.ibb.co/S0t5GWb/imglogo.png" height='80' width='90' vspace='-10'>
        """)

    df_div1 = hv.Div("""
        &nbsp<center><b><p style="color:#B22222";font-size:80px;font-family:Times new roman><h1 style=font-size:20px;margin-left:2.5em;margin-top:-1em;color:#B22222>Indian National Center for Ocean Information Services<br />
        (INCOIS)</h1></p></b></center>

        """)
    df_div2 = hv.Div("""
            <html>
            <head>
            <style>
            input[type=button], input[type=submit], input[type=reset] {
              background-color: #C6E2FF;
              color: DARKVIOLET;
              padding: 10px 22px;
              text-decoration: none;
              margin: 4px 2px;
              cursor: pointer;
              font-weight: bold;
              font-size: 15px;
              border: 2px solid light slateblue
            }
            </style>
            </head>
            <body>

            <input type="button" value=" PRINT " onClick="window.print()">


            </body>
            </html>

            """)

    colorbar_opts = {
        'major_label_overrides': {
            0.00: '0.00',
            0.02: '0.02',

            0.04: '0.04',

            0.06: '0.06',

            0.08: '0.08',

            0.10: '0.10',

            0.12: '0.12',
            0.14: '> 0.14',

            0.15: '0.15',
            0.16: ' ',
            0.17: '>0.17',

        },
        'major_label_text_align': 'left', 'major_label_text_font_style': 'bold', }
    levels = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.15, 0.16, 0.17]

    def disable_logo(plot, element):
        plot.state.toolbar.logo = None

    hv.plotting.bokeh.ElementPlot.finalize_hooks.append(disable_logo)

    def plot_limits(plot, element):
        plot.handles['x_range'].min_interval = 100
        plot.handles['x_range'].max_interval = 55000000
        # 3000000
        plot.handles['y_range'].min_interval = 500
        plot.handles['y_range'].max_interval = 900000

    opts = dict(width=700, height=700, logz=False, logx=False, logy=False, responsive=True, active_tools=['wheel_zoom'],
                tools=['save', 'wheel_zoom', 'hover'], hooks=[plot_limits, disable_logo], colorbar=True,
                color_levels=15,
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

                                                   ], clim=(0.00, 0.15), title="\t\t\t\t\t\t\t\t Wave Steepness  . ",
                fontsize={'title': 18, 'xlabel': 15, 'ylabel': 15, 'ticks': 12})

    tiles = gv.tile_sources.Wikipedia
    tiles = gv.tile_sources.Wikipedia
    hmap1 = hv.HoloMap(allplot, kdims=['Select Date and Time :', 'Select Indian States'])
    # hmap2 = hv.HoloMap(allplot2, kdims=['Date and Time :','region'])
    logo1 = hv.RGB.load_image("https://i.ibb.co/7VXRPCS/logo1.png")

    def absolute_position(plot, element):
        glyph = plot.handles['glyph']
        x_range, y_range = plot.handles['x_range'], plot.handles['y_range']
        glyph.dh_units = 'screen'
        glyph.dw_units = 'screen'
        glyph.dh = 60
        glyph.dw = 90
        #     x_range.start=+85
        #     y_range.start=+20
        glyph.x = x_range.start
        glyph.y = y_range.start
        xcode = CustomJS(code="glyph.x = cb_obj.start", args={'glyph': glyph})
        plot.handles['x_range'].js_on_change('start', xcode)
        ycode = CustomJS(code="glyph.y = cb_obj.start", args={'glyph': glyph})
        plot.handles['y_range'].js_on_change('start', ycode)

    # finalplot=tiles*rasterize(hmap1.redim.range(Latitude=(13, 19), Longitude=(79, 85))).options(**opts)*hmap2

    dd = df_div.opts(width=90, height=80)
    dd1 = df_div1.opts(width=600, height=90)
    dd2 = df_div2.opts(width=100, height=10)

    finalplot = pn.Column(pn.Row(dd, dd1),
                          tiles * rasterize(hmap1).options(**opts) * logo1.opts(hooks=[absolute_position],
                                                                                        apply_ranges=False))
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