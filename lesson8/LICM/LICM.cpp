#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/IR/IRBuilder.h"

#include "llvm/Analysis/LoopPass.h"
#include "llvm/Analysis/LoopInfo.h"
#include "llvm/Transforms/Utils.h"

#include <set>
using namespace llvm;

namespace {
    struct LICMPass : public LoopPass {
        static char ID;
        LICMPass() : LoopPass(ID) {}

        virtual bool runOnLoop(Loop *L, LPPassManager &LPM) {

            bool changed = false;
            bool found_invariant = true;

            while (found_invariant) { // if we don't find an invariant, we're done
                found_invariant = false;
                // errs() << "Loop: " << L->getName() << "\n"; // Loop: <unnamed loop>
                errs() << "Iteration begin......\n";

                for (auto bit = L->block_begin(); bit != L->block_end(); bit++) { // llvm::BasicBLock *const *bit
                    // errs() << **bit << "\n";
                    for (auto &I : **bit) {
                        // errs() << "Instruction: " << I << "\n";
                        
                        bool is_invariant = false;

                        // Return true if I is already loop-invariant, and false if I can't be made loop-invariant.
                        // If I is made loop-invariant, Changed is set to true. 
                        L->makeLoopInvariant(&I, is_invariant);

                        // errs() << I << "\n";
                        // errs() << "is_variant: " << is_invariant << "\n\n";

                        if (is_invariant) {
                            errs() << "Found invariant " << I << "\n";
                            errs() << "This Iteration is done!\n\n";
                            found_invariant = true;
                            break; // break to the outer while loop
                        }

                        changed = changed || is_invariant;
                    }

                    if (found_invariant) { 
                        break; // break to the outer while loop
                    }
                }

            }

            return changed;
        }                    
    };
}

char LICMPass::ID = 0;

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerLICMPass(const PassManagerBuilder &,
                            legacy::PassManagerBase &PM) {
    // PM.add(createPromoteMemoryToRegisterPass());
    PM.add(new LICMPass());
}
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                    registerLICMPass);
