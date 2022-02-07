######################################
#
# max-gen-plugin
#
######################################

MAX_GEN_PLUGIN_VERSION = 1
MAX_GEN_PLUGIN_SITE_METHOD = local
MAX_GEN_PLUGIN_SITE = $($(PKG)_PKGDIR)/
MAX_GEN_PLUGIN_DEPENDENCIES = max-gen-template
MAX_GEN_PLUGIN_PLUGIN_NAME = @pluginame@

$(eval $(generic-package))
