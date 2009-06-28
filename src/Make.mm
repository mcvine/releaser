PROJECT = mcvine


PROJ_TIDY += *.log *.tmp

# directory structure


BUILD_DIRS = \
	config \
	pyre \
	pyregui \
	dsm \
	numpyext \
	bpext \
	luban \
	histogram \
	crystal \
	hdf5fs \
	nx5 \
	instrument \
	sampleassembly \
	mcvine \
	sansmodels \



RECURSE_DIRS = $(BUILD_DIRS)

#--------------------------------------------------------------------------
#

all: 
	BLD_ACTION="all" $(MM) recurse

distclean::
	BLD_ACTION="distclean" $(MM) recurse

clean::
	BLD_ACTION="clean" $(MM) recurse

tidy::
	BLD_ACTION="tidy" $(MM) recurse

docs::
	BLD_ACTION="docs" $(MM) recurse

# version
# $Id: Make.mm 1363 2007-07-29 14:24:24Z linjiao $

# End of file
