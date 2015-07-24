#!/usr/bin/env python
# FastHeader.py encoded in UTF-8
# Project : FastHeader
# Contact : info@devolive.be
# Created by olive007 at 17/07/2015 19:58:06
# Last update by olive007 at 24/07/2015 19:09:51

import os, re, getpass, time
import sublime, sublime_plugin

PLUGIN_NAME = "FastHeader"
PLUGIN_PATH = os.path.join(sublime.packages_path(), PLUGIN_NAME)
HEADER_TEMPLATE_PATH = os.path.join(PLUGIN_PATH, "HeaderTemplates")

def plugin_loaded():
	global PLUGIN_NAME
	global PLUGIN_PATH
	global HEADER_TEMPLATE_PATH

	PLUGIN_NAME = "FastHeader"
	PLUGIN_PATH = os.path.join(sublime.packages_path(), PLUGIN_NAME)
	HEADER_TEMPLATE_PATH = os.path.join(PLUGIN_PATH, "HeaderTemplates")

def get_settings():
	return sublime.load_settings("%s.sublime-settings" % PLUGIN_NAME)

def get_syntax(file_name):
	syntax = 'undefined'

	file_mapping = get_settings().get('file_mapping')

	for key in file_mapping:
		mapping = re.compile(key)
		if (mapping.match(file_name)):
			syntax = file_mapping[key]

	return syntax

def get_header_template(syntax):
	template = 'undefined'
	
	header_file = ""
	project = sublime.active_window().project_data()
	
	if project:
		if 'fastHeader' in project.keys():
			custom_template_dir = project['fastHeader']
			if custom_template_dir is None or len(custom_template_dir)!= 0:
				file_name = os.path.join(custom_template_dir, ("%s.template" % syntax))
				if os.path.isfile(file_name):
					header_file = file_name

	if header_file == "":
		header_file = os.path.join(HEADER_TEMPLATE_PATH, ("%s.template" % syntax))

	file = open(header_file, 'r')
	template = file.read()
	file.close()

	return template

def get_author():
	author = get_settings().get('author')

	if author is None or len(author) == 0:
		author = getpass.getuser()
	return author

def get_date():
	return time.strftime(get_settings().get("time_format"))

def get_file_name():
	return os.path.basename(sublime.active_window().active_view().file_name())

def get_file_name_without_extension():
	return ('.').join(get_file_name().split('.')[:-1])

def get_file_path():
	return os.path.basename(sublime.active_window().active_view().file_name())

def get_project_name():
	project = sublime.active_window().project_data()
	if project is None:
		return "No Project"
	else:
		project_name = project.get("name")
		if project_name is None:
			return ""
	return project_name

def get_encoding():
	return sublime.active_window().active_view().encoding()

def get_custom_variable(name):
	return get_settings().get("variable").get(name)

def get_custom_variable_regex(name):
	return get_settings().get("variable_regex").get(name)

def get_beginning(view):
	syntax = get_syntax(os.path.basename(view.file_name()))

	try:
		template = get_header_template(syntax)
	except Exception as e:
		sublime.error_message("Error : template for %s not found" % syntax)
		return

	lines = template.split("\n")
	nb_line_template = len(lines)
	max_line_lenght = get_settings().get("max_line_lenght")
	
	beginning = view.substr(sublime.Region(0, nb_line_template * max_line_lenght))
	lines = beginning.split('\n')
	del lines[nb_line_template:]
	
	beginning = "\n".join(lines)
	return beginning


def regex_template(template):
	def doAuthor(line, res, uptading=False):
		if not uptading:
			return "%s%s%s" % (line[:res.start(0)], "(.+)", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], ".+", line[res.end(0):])

	def doDate(line, res, uptading=False):
		regex = get_settings().get("time_format_regex")
		if not uptading:
			return "%s%s%s%s%s" % (line[:res.start(0)], "(", regex, ")", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], regex, line[res.end(0):])

	def doFileName(line, res, uptading=False):
		if not uptading:
			return "%s%s%s" % (line[:res.start(0)], "(.+)", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], ".+", line[res.end(0):])

	def doFileNameWithoutExtend(line, res, uptading=False):
		if not uptading:
			return "%s%s%s" % (line[:res.start(0)], "(.+)", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], ".+", line[res.end(0):])

	def doFilePath(line, res, uptading=False):
		if not uptading:
			return "%s%s%s" % (line[:res.start(0)], "(.+)", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], ".+", line[res.end(0):])

	def doProjectName(line, res, uptading=False):
		if not uptading:
			return "%s%s%s" % (line[:res.start(0)], "(.*)", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], ".*", line[res.end(0):])

	def doEncoding(line, res, uptading=False):
		if not uptading:
			return "%s%s%s" % (line[:res.start(0)], "(.+)", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], ".+", line[res.end(0):])

	def doCustomVar(line, res, uptading=False):
		var_name = res.group(1)
		regex = get_custom_variable_regex(var_name)
		if not uptading:
			return "%s%s%s%s%s" % (line[:res.start(0)], "(", regex, ")", line[res.end(0):])
		return "%s%s%s" % (line[:res.start(0)], regex, line[res.end(0):])

	regex = ""
	new_actions = (
		(re.compile("{{author}}"), doAuthor),
		(re.compile("{{date}}"), doDate),
		(re.compile("{{fileName}}"), doFileName),
		(re.compile("{{fileNameWithoutExtend}}"), doFileNameWithoutExtend),
		(re.compile("{{filePath}}"), doFilePath),
		(re.compile("{{projectName}}"), doProjectName),
		(re.compile("{{encoding}}"), doEncoding),
		(re.compile("{{(.*)}}"), doCustomVar)
	)
	update_actions = (
		(re.compile("\[\[author\]\]"), doAuthor),
		(re.compile("\[\[date\]\]"), doDate),
		(re.compile("\[\[fileName\]\]"), doFileName),
		(re.compile("\[\[fileNameWithoutExtend\]\]"), doFileNameWithoutExtend),
		(re.compile("\[\[filePath\]\]"), doFilePath),
		(re.compile("\[\[projectName\]\]"), doProjectName),
		(re.compile("\[\[encoding\]\]"), doEncoding),
		(re.compile("\[\[(.*)\]\]"), doCustomVar)
	)

	template = template.replace('\\', "\\\\")
	template = template.replace('.', "\.")
	template = template.replace('^', "\^")
	template = template.replace('$', "\$")
	template = template.replace('*', "\*")
	template = template.replace('+', "\+")
	template = template.replace('?', "\?")
	template = template.replace('|', "\|")

	lines = template.split('\n')
	i = 0
	for line in lines:
		for reg, action in new_actions:
			res = reg.search(line)
			if res:
				line = action(line, res)
		for reg, action in update_actions:
			res = reg.search(line)
			if res:
				line = action(line, res, True)
		if len(lines) - 1 != i:
			regex += "^"+line+"$\n"
		else:
			regex += "^"+line
		i += 1
	
	return regex

def render_template(template, beginning=''):

	def doAuthor(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_author(), line[res.end(0):])

	def doDate(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_date(), line[res.end(0):])

	def doFileName(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_file_name(), line[res.end(0):])

	def doFileNameWithoutExtend(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_file_name_without_extension(), line[res.end(0):])

	def doFilePath(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_file_path(), line[res.end(0):])

	def doProjectName(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_project_name(), line[res.end(0):])

	def doEncoding(line, res):
		return "%s%s%s" % (line[:res.start(0)], get_encoding(), line[res.end(0):])

	def doCustomVar(line, res):
		var_name = res.group(1)
		return "%s%s%s" % (line[:res.start(0)], get_custom_variable(var_name), line[res.end(0):])

	render = ""
	new_actions = (
		(re.compile("{{author}}"), doAuthor),
		(re.compile("{{date}}"), doDate),
		(re.compile("{{fileName}}"), doFileName),
		(re.compile("{{fileNameWithoutExtend}}"), doFileNameWithoutExtend),
		(re.compile("{{filePath}}"), doFilePath),
		(re.compile("{{projectName}}"), doProjectName),
		(re.compile("{{encoding}}"), doEncoding),
		(re.compile("{{(.*)}}"), doCustomVar)
	)
	update_actions = (
		(re.compile("\[\[author\]\]"), doAuthor),
		(re.compile("\[\[date\]\]"), doDate),
		(re.compile("\[\[fileName\]\]"), doFileName),
		(re.compile("\[\[fileNameWithoutExtend\]\]"), doFileNameWithoutExtend),
		(re.compile("\[\[filePath\]\]"), doFilePath),
		(re.compile("\[\[projectName\]\]"), doProjectName),
		(re.compile("\[\[encoding\]\]"), doEncoding),
		(re.compile("\[\[(.*)\]\]"), doCustomVar)
	)

	max_line_lenght = get_settings().get("max_line_lenght")

	template_line = template.split('\n')
	old_line = beginning.split('\n')
	regex_line = regex_template(template).split('\n')

	i = 0
	while (i < len(template_line)):
		for regex, action in update_actions:
			res = regex.search(template_line[i])
			if res:
				template_line[i] = action(template_line[i], res)
		j = 1
		for regex, action in new_actions:
			template_res = regex.search(template_line[i])
			if template_res:
				if len(beginning) != 0:
					regex_res = re.match(regex_line[i], old_line[i])
					template_line[i] = "%s%s%s" % (template_line[i][:template_res.start(0)], old_line[i][regex_res.start(j) : regex_res.end(j)], template_line[i][template_res.end(0):])
					j += 1
				else:
					template_line[i] = action(template_line[i], template_res)
		if len(template_line[i]) > max_line_lenght:
			template_line[i] = template_line[i][:max_line_lenght]
		if i != len(template_line) - 1:
			render += template_line[i] + "\n"
		else:
			if len(beginning) != 0:
				res = re.match(regex_line[i], old_line[i])
				render += template_line[i] + old_line[i][res.end(0):]
			else:
				render += template_line[i]
		i += 1
	return render

def header_is_present(view):
	present = False
	syntax = get_syntax(os.path.basename(view.file_name()))

	try:
		template = get_header_template(syntax)
	except Exception as e:
		sublime.error_message("Error : template for %s not found" % syntax)
		return
	
	beginning = get_beginning(view)

	if (re.match(regex_template(template), beginning, re.MULTILINE)):
		present = True

	return present


class fast_header_addCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		file_name = os.path.basename(sublime.active_window().active_view().file_name())
		file_syntax = get_syntax(file_name)

		if file_syntax is not 'undefined':
			print("Add header type '%s' in file '%s'" % (file_syntax, file_name))

			try:
				template = get_header_template(file_syntax)
			except Exception as e:
				sublime.error_message("Error : template for %s not found" % file_syntax)
				return

			template_render = render_template(template)
			self.view.insert(edit, 0, template_render)



class fast_header_updateCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		file_name = get_file_name()
		file_syntax = get_syntax(file_name)

		if file_syntax is not 'undefined':
			if header_is_present(sublime.active_window().active_view()):
				print("Update header type '%s' in file '%s'" % (file_syntax, file_name))

				try:
					template = get_header_template(file_syntax)
				except Exception as e:
					sublime.error_message("Error : template for %s not found" % file_syntax)
					return

				beginning = get_beginning(sublime.active_window().active_view())

				template_render = render_template(template, beginning)
				region = sublime.Region(0, len(beginning))
				self.view.replace(edit, region, template_render)



class FastHeaderEvent(sublime_plugin.EventListener):
	
	new_view_id = []

	def on_new(self, view):
		FastHeaderEvent.new_view_id.append(view.id())

	def on_pre_save(self, view):
		if view.is_dirty():
			file_name = get_file_name()
			file_syntax = get_syntax(file_name)

			if get_settings().get("activated") == True:
				if file_syntax is not 'undefined':
					view.run_command('fast_header_update')

	def on_post_save(self, view):
		if get_settings().get("activated") == True and view.id() in FastHeaderEvent.new_view_id:
			view.run_command('fast_header_add')
			if get_syntax(get_file_name()) is not 'undefined':
				FastHeaderEvent.new_view_id.remove(view.id())
