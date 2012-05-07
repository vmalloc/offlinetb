function offlinetb_render(offline_tb, container) {
    var div = $('<div class="offlinetb"></div>');
    div.append(offlinetb_format_exception(offline_tb.exception));
    var tb_div = $('<div class="offlinetb-traceback"></div>');
    tb_div.append(offlinetb_format_tb(offline_tb.traceback));
    div.append(tb_div);
    container.append(div);
}

function offlinetb_format_exception(exception) {
    var returned = $('<div class="offlinetb-exception"></div>');
    returned.text("Exception: " + exception.type + " (" + exception.value + ")");
    returned.data('vars', exception.vars);
    returned.click(offlinetb_open_vars);
    return returned;
}

function offlinetb_format_tb(traceback) {
    var traceback_div = $("<div></div>");
    for (var i = 0; i < traceback.length; ++i) {
        var frame = offlinetb_format_frame(traceback[i])
        traceback_div.append(frame);
        if (i == traceback.length - 1) {
            frame.addClass("expanded");
            frame.find(".offlinetb-lines-before, .offlinetb-lines-after, .offlinetb-show-vars-btn").show();
        }
    }
    return traceback_div;
}

function offlinetb_format_frame(frame) {
    var frame_div = $('<div class="offlinetb-frame"></div>');
    frame_div.append(offlinetb_format_frame_info(frame));
    frame_div.append(offlinetb_format_frame_lines(frame));
    frame_div.append(offlinetb_format_show_vars_button(frame));
    frame_div.click(function() {
        frame_div.toggleClass('expanded');
        var buttons = frame_div.find(".offlinetb-show-vars-btn");
        var is_expanded = frame_div.hasClass('expanded');
        var lines = frame_div.find(".offlinetb-lines-after, .offlinetb-lines-before").each(function() {
            var lines = $(this);
            if (is_expanded) {
                lines.slideDown('fast');
                buttons.slideDown('fast');
            } else {
                lines.slideUp('fast');
                buttons.slideUp('fast');
            }
        });
        
    });
    return frame_div;
}

function offlinetb_format_frame_info(frame) {
    var frame_info = $('<div class="offlinetb-frame-info"></div>');
    frame_info.text(frame.filename + ", in " + frame['function']);
    return frame_info;
}

function offlinetb_format_frame_lines(frame) {
    var returned = $('<div class="offlinetb-lines"></div>');
    var lines_before = $('<div class="offlinetb-lines-before"></div>');
    var lines_after  = $('<div class="offlinetb-lines-after"></div>');
    lines_before.hide();
    lines_after.hide();
    returned.append(lines_before);
    _offlinetb_add_lines(frame.lineno - frame.lines_before.length, frame.lines_before, lines_before);
    _offlinetb_add_line(frame.lineno, frame.line, returned).addClass('offlinetb-faulty');
    returned.append(lines_after);
    _offlinetb_add_lines(frame.lineno + 1, frame.lines_after, lines_after);
    return returned;
}

function offlinetb_format_show_vars_button(frame) {
    var button = $('<div class="offlinetb-btn offlinetb-show-vars-btn">Show local variables...</div>');
    button.click(offlinetb_open_vars);
    button.hide();
    button.data("vars", frame.vars);
    return button;
}

function _offlinetb_add_lines(start_lineno, lines, lines_div, line_class) {
    for (var i = 0; i < lines.length; ++i) {
        var line = $('<div class="offlinetb-line"></div>');
        line.addClass(line_class);
        line.text(start_lineno + '. ' + lines[i]);
        lines_div.append(line)
        start_lineno++;
    }

    return line;
}

function _offlinetb_add_line(start_lineno, line, lines_div, line_class) {
    return _offlinetb_add_lines(start_lineno, [line], lines_div, line_class);
}

function offlinetb_open_vars(evt) {
    var button = $(this);
    evt.stopPropagation();
    var vars = button.data('vars');
    var open_variables = button.find(".offlinetb-vars")
    if (open_variables.length > 0) {
        open_variables.slideUp('fast', function () {
            open_variables.remove();
        });
    }
    else {
        var vars_div = $('<div class="offlinetb-vars"></div>');
        vars_div.hide();
        vars_div.append(offlinetb_format_vars_table(vars));
        vars_div.appendTo(button);
        vars_div.slideDown('fast');
    }
}

function _offlinetb_append_element(container, e) {
    e = $(e);
    container.append(e);
    return e;
}

function offlinetb_format_vars_table(vars) {
    var returned = $('<table class="offlinetb-vars-table"><thead><tr><th>Name</th><th>Value</th></tr></thead></table>');
    for (var i = 0; i < vars.length; ++i) {
        var v = $('<tr></tr>');
        _offlinetb_append_cell(v, vars[i].name);
        var value_td = _offlinetb_append_cell(v, vars[i].value);
        if (vars[i].hasOwnProperty('vars') && vars[i]['vars'] != null && vars[i]['vars'].length > 0) {
            value_td.addClass('offlinetb-expandable-variable-btn');
            value_td.append(" &rarr;")
            value_td.data('vars', vars[i].vars);
            value_td.click(offlinetb_open_vars);
        }
        returned.append(v);
    }
    return returned;
}

function _offlinetb_append_cell(tr, text) {
    var td = $("<td></td>");
    td.text(text);
    td.appendTo(tr);
    return td;
}
