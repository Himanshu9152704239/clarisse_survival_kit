import os
import re
import logging

from clarisse_survival_kit.settings import *


def add_gradient_key(attr, position, color, **kwargs):
    """
    Create a key in the specified gradient attribute with the given position and color.
    If the given color is an array of 3 elements, a 4th is added to have the alpha chanel set to 1.0

    :param attr: The attribute of the gradient for example: <!-- m --><a class="postlink" href="project://gradient.output">project://gradient.output</a><!-- m -->
    :type attr: string or PyOfObject

    :param position: The position of the key you want to set
    :type position: float

    :param color: The color you want to set on the point for example [1, 0, 0] for red
    :type color: list of int

    :return: True or false depending on the sucess of the function.
    """
    ix = get_ix(kwargs.get("ix"))
    if isinstance(attr, str):
        attr = ix.item_exists(attr)
    if not attr:
        ix.log_warning("The specified attribute doesn't exists.")
        return False

    data = []
    if len(color) == 3:
        color.append(1)

    for i in range(len(color)):
        data.append(1.0)
        data.append(0.0)
        data.append(position)
        data.append(float(color[i]))

    ix.cmds.AddCurveValue([str(attr)], data)

    return True


def get_ix(ix_local):
    """Simple function to check if ix is imported or not."""
    try:
        ix
    except NameError:
        return ix_local
    else:
        return ix


def get_textures_from_directory(directory, filename_match_template=FILENAME_MATCH_TEMPLATE,
                                image_formats=IMAGE_FORMATS):
    """Returns texture files which exist in the specified directory."""
    logging.debug("Searching for textures inside: " + str(directory))
    textures = {}
    for root, dirs, files in os.walk(directory):
        for f in files:
            filename, extension = os.path.splitext(f)
            extension = extension.lower().lstrip('.')
            if extension in image_formats:
                logging.debug("Found image: " + str(f))
                path = os.path.normpath(os.path.join(root, f))
                for key, pattern in filename_match_template.iteritems():
                    match = re.search(pattern, filename, re.IGNORECASE)
                    if match:
                        logging.debug("Image matches with: " + str(key))
                        if key == 'normal_lods':
                            if type(textures.get(key)) != list:
                                textures[key] = []
                            else:
                                # Check if another file extension exists.
                                # If so use the first that occurs in the image_formats list.
                                previous_extension = os.path.splitext(textures[key][-1])[-1].lstrip('.')
                                if image_formats.index(previous_extension) > image_formats.index(extension):
                                    textures[key] = path
                                    continue
                            textures[key].append(path)
                        else:
                            # Check if another file extension exists.
                            # If so use the first that occurs in the image_formats list.
                            if key in textures:
                                previous_extension = os.path.splitext(textures[key])[-1].lstrip('.')
                                if image_formats.index(previous_extension) > image_formats.index(extension):
                                    textures[key] = path
                            else:
                                textures[key] = path
    if textures:
        logging.debug("Textures found in directory: " + directory)
        logging.debug(str(textures))
    else:
        logging.debug("No textures found in directory.")
    return textures


def get_geometry_from_directory(directory):
    """Returns texture files which exist in the specified directory."""
    logging.debug("Searching for meshes inside: " + str(directory))
    meshes = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.obj', '.abc', '.lwo')):
                logging.debug("Found mesh file: " + str(filename))
                path = os.path.join(root, filename)
                path = os.path.normpath(path)
                meshes.append(path)
    if meshes:
        logging.debug("Meshes found in directory: " + directory)
        logging.debug(str(meshes))
    else:
        logging.debug("No meshes found in directory.")
    return meshes


def get_stream_map_files(textures):
    """"Returns the files that should be loaded as TextureStreamedMapFile."""
    logging.debug("Searching for streamed map files...")
    stream_map_files = []
    if not textures:
        return []
    for index, texture in textures.iteritems():
        logging.debug("Testing: " + str(textures))
        if type(texture) == list:
            items = get_stream_map_files({str(i): texture[i] for i in range(0, len(texture))})
            for item in items:
                stream_map_files.append(item)
        else:
            filename, extension = os.path.splitext(texture)
            extension = extension.lower().lstrip('.')

            udim_match = re.search(r"((?<!\d)\d{4}(?!\d))", os.path.split(filename)[-1])
            if udim_match or extension == "tx":
                logging.debug("Streamed map file found.")
                stream_map_files.append(index)
    if stream_map_files:
        logging.debug("...found these streamed map files: ")
        logging.debug(str(stream_map_files))
    else:
        logging.debug("...no streamed map files found.")
    return stream_map_files


def get_mtl_from_context(ctx, **kwargs):
    """"Returns the material from the context."""
    ix = get_ix(kwargs.get("ix"))
    objects_array = ix.api.OfObjectArray(ctx.get_object_count())
    flags = ix.api.CoreBitFieldHelper()
    ctx.get_all_objects(objects_array, flags, False)
    mtl = None
    for ctx_member in objects_array:
        if check_selection([ctx_member], is_kindof=["MaterialPhysicalStandard", "MaterialPhysicalBlend"], max_num=1):
            if ctx_member.is_local() and ctx_member.get_contextual_name().endswith(MATERIAL_SUFFIX) or not mtl:
                mtl = ctx_member
    if not mtl:
        logging.debug("No material found in ctx: " + str(ctx))
        return None
    logging.debug("Found material: " + str(mtl))
    return mtl


def get_disp_from_context(ctx, **kwargs):
    """"Returns the material from the context."""
    ix = get_ix(kwargs.get("ix"))
    objects_array = ix.api.OfObjectArray(ctx.get_object_count())
    flags = ix.api.CoreBitFieldHelper()
    ctx.get_all_objects(objects_array, flags, False)
    disp = None
    for ctx_member in objects_array:
        if check_selection([ctx_member], is_kindof=["Displacement"], max_num=1):
            if ctx_member.is_local() and ctx_member.get_contextual_name().endswith(DISPLACEMENT_MAP_SUFFIX) or not disp:
                disp = ctx_member
    if not disp:
        logging.debug("No displacement found in ctx: " + str(ctx))
        return None
    logging.debug("Found displacement: " + str(disp))
    return disp


def get_attrs_connected_to_texture(texture_item, connected_attrs, **kwargs):
    """
    This searches for occourences of the selected texture item in other textures.
    Original function was written by Isotropix. I made a modification so it also searches for strings.
    The MaterialPhysicalBlend doesn't use SetTextures(), but SetValues().
    The only way to retrieve the connected values were by using get_string().
    """
    ix = get_ix(kwargs.get("ix"))
    # Script by Isotropix
    # temporary variables needed to call get_items_outputs on the factory
    items = ix.api.OfItemArray(1)
    items[0] = texture_item
    output_items = ix.api.OfItemVector()

    # let's call the get_items_outputs like in the context selection toolbar;
    # last parameter 'False' means no recursivity on getting dependencies
    ix.application.get_factory().get_items_outputs(items, output_items, False)

    # checks retrieved dependencies
    for i_output in range(0, output_items.get_count()):
        out_item = output_items[i_output]
        if out_item.is_object():
            out_obj = out_item.to_object()
            attr_count = out_obj.get_attribute_count()
            for i_attr in range(0, attr_count):
                attr = out_obj.get_attribute(i_attr)
                if (attr.is_textured() and str(attr.get_texture()) == str(texture_item)) or \
                        (attr.get_string() == str(texture_item)):
                    connected_attrs.add(attr)


def get_textures_connected_to_texture(texture_item, **kwargs):
    """Returns the connected textures to the specified texture as a list."""
    ix = get_ix(kwargs.get("ix"))
    # Script by Isotropix
    # temporary variables needed to call get_items_outputs on the factory
    items = ix.api.OfItemArray(1)
    items[0] = texture_item
    output_items = ix.api.OfItemVector()

    # let's call the get_items_outputs like in the context selection toolbar;
    # last parameter 'False' means no recursivity on getting dependencies
    ix.application.get_factory().get_items_outputs(items, output_items, False)

    # checks retrieved dependencies
    textures = []
    for i_output in range(0, output_items.get_count()):
        out_item = output_items[i_output]
        if out_item.is_object():
            out_obj = out_item.to_object()
            textures.append(out_obj)
    return textures


def check_selection(selection, is_kindof=[""], max_num=0, min_num=1):
    """Simple function to check the kind of objects selected and to limit selection."""
    num = 0
    for item in selection:
        pass_test = False
        for kind in is_kindof:
            if item.is_context():
                if kind == "OfContext":
                    pass_test = True
                    break
            elif item.is_kindof(kind):
                pass_test = True
                break
            elif kind in item.get_class_name():
                pass_test = True
                break
        if not pass_test:
            return False
        else:
            num += 1
    if num < min_num:
        return False
    elif max_num and num > max_num:
        return False
    return True


def check_context(ctx, **kwargs):
    """Tests if you can write to specified context."""
    ix = get_ix(kwargs.get("ix"))
    if (not ctx.is_editable()) or ctx.is_content_locked() or ctx.is_remote():
        ix.log_warning("Cannot write to context, because it's locked.")
        return False
    return True


def get_sub_contexts(ctx, name="", max_depth=0, current_depth=0, **kwargs):
    """Gets all subcontexts."""
    ix = get_ix(kwargs.get("ix"))
    current_depth += 1
    results = []
    for i in range(ctx.get_context_count()):
        sub_context = ctx.get_context(i)
        results.append(sub_context)
        # 0 is infinite
        if current_depth <= max_depth or max_depth == 0:
            for result in get_sub_contexts(sub_context, name, max_depth, current_depth, ix=ix):
                if result not in results:
                    results.append(result)
    if name:
        for sub_ctx in results:
            if os.path.basename(str(sub_ctx)) == name:
                return sub_ctx
        return []
    return results


def get_items(ctx, kind=None, max_depth=0, current_depth=0, **kwargs):
    """Gets all items recursively."""
    ix = get_ix(kwargs.get("ix"))
    result = []
    items = ix.api.OfItemVector()
    sub_ctxs = get_sub_contexts(ctx, max_depth=max_depth, current_depth=current_depth, ix=ix)
    sub_ctxs.insert(0, ctx)
    for sub_ctx in sub_ctxs:
        if sub_ctx.get_object_count():
            objects_array = ix.api.OfObjectArray(sub_ctx.get_object_count())
            flags = ix.api.CoreBitFieldHelper()
            sub_ctx.get_all_objects(objects_array, flags, False)
            for i_obj in range(sub_ctx.get_object_count()):
                if kind is not None:
                    if objects_array[i_obj].is_kindof(kind):
                        items.add(objects_array[i_obj])
                else:
                    items.add(objects_array[i_obj])
    for item in items:
        result.append(item)
    return result


def tx_to_triplanar(tx, blend=0.5, object_space=0, **kwargs):
    """Converts the texture to triplanar."""
    logging.debug("Converting texture to triplanar: " + str(tx))
    ix = get_ix(kwargs.get("ix"))
    print "Triplanar Blend: " + str(blend)
    ctx = tx.get_context()
    triplanar = ix.cmds.CreateObject(tx.get_contextual_name() + TRIPLANAR_SUFFIX, "TextureTriplanar", "Global",
                                     str(ctx))
    connected_attrs = ix.api.OfAttrVector()

    get_attrs_connected_to_texture(tx, connected_attrs, ix=ix)

    for i_attr in range(0, connected_attrs.get_count()):
        ix.cmds.SetTexture([str(connected_attrs[i_attr])], str(triplanar))
    ix.cmds.SetTexture([str(triplanar) + ".right"], str(tx))
    ix.cmds.SetTexture([str(triplanar) + ".left"], str(tx))
    ix.cmds.SetTexture([str(triplanar) + ".top"], str(tx))
    ix.cmds.SetTexture([str(triplanar) + ".bottom"], str(tx))
    ix.cmds.SetTexture([str(triplanar) + ".front"], str(tx))
    ix.cmds.SetTexture([str(triplanar) + ".back"], str(tx))
    ix.cmds.SetValues([str(triplanar) + '.blend', str(triplanar) + '.object_space'],
                      [str(blend), str(object_space)])
    return triplanar


def blur_tx(tx, radius=0.01, quality=DEFAULT_BLUR_QUALITY, **kwargs):
    """Blurs the texture."""
    logging.debug("Blurring selected texture: " + str(tx))
    ix = get_ix(kwargs.get("ix"))
    ctx = tx.get_context()
    blur = ix.cmds.CreateObject(tx.get_contextual_name() + BLUR_SUFFIX, "TextureBlur", "Global", str(ctx))

    connected_attrs = ix.api.OfAttrVector()

    get_attrs_connected_to_texture(tx, connected_attrs, ix=ix)

    for i_attr in range(0, connected_attrs.get_count()):
        ix.cmds.SetTexture([connected_attrs[i_attr].get_full_name()], blur.get_full_name())
    ix.cmds.SetTexture([str(blur) + ".color"], str(tx))
    blur.attrs.radius = radius
    blur.attrs.quality = quality
    return blur