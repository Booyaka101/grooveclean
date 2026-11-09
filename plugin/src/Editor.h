#pragma once

#include "public.sdk/source/vst/vsteditcontroller.h"

namespace groove {
Steinberg::IPlugView* createEditor(Steinberg::Vst::EditController* controller);
}
