from matplotlib import pyplot as plt


def zoom_factory(ax, data_viz_control, base_scale=2.):
    def zoom_fun(event):

        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)
        # set new limits
        # ax.set_xlim([xdata - (xdata-cur_xlim[0]) / scale_factor,
        #             xdata + (cur_xlim[1]-xdata) / scale_factor])
        min_lower_xlim = data_viz_control.min_lower_xlim
        max_upper_xlim = data_viz_control.max_upper_xlim

        xlim = [xdata - (xdata-cur_xlim[0]) / scale_factor,
                xdata + (cur_xlim[1]-xdata) / scale_factor]

        if xlim[0] < min_lower_xlim:
            xlim[0] = min_lower_xlim
        if xlim[1] > max_upper_xlim:
            xlim[1] = max_upper_xlim

        ax.set_xlim(xlim)

        data_viz_control.xlim = xlim

        plt.draw()  # force re-draw

    fig = ax.get_figure()  # get the figure of interest
    # attach the call back
    fig.canvas.mpl_connect('scroll_event', zoom_fun)

    # return the function
    return zoom_fun
