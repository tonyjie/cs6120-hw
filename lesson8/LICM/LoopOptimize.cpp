#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/IR/IRBuilder.h"

// #include "llvm/Analysis/LoopPass.h"
#include "llvm/Analysis/LoopInfo.h"
using namespace llvm;

namespace {
    struct LoopOptimizePass : public FunctionPass {
        static char ID;
        LoopOptimizePass() : FunctionPass(ID) {}

        void getAnalysisUsage(AnalysisUsage &AU) const {
            AU.addRequired<LoopInfoWrapperPass>();
            AU.setPreservesAll();
        }

        void countBlocksInLoop(Loop *L, unsigned nesting) {
            unsigned numBlocks = 0;
            for (auto bb = L->block_begin(); bb != L->block_end(); ++bb) {
                numBlocks++;
            }
            errs() << "Loop Level " << nesting << " has " << numBlocks << " blocks\n";
            
            std::vector<Loop*> subLoops = L->getSubLoops();
            for (auto j = subLoops.begin(), f = subLoops.end(); j != f; ++j) {
                countBlocksInLoop(*j, nesting + 1);
            }
        }

        virtual bool runOnFunction(Function &F) {
            LoopInfo &LI = getAnalysis<LoopInfoWrapperPass>().getLoopInfo();
            int LoopCounter = 0;
            errs() << F.getName() + "\n";

            for (auto i = LI.begin(), e = LI.end(); i != e; ++i) {
                countBlocksInLoop(*i, 0);
            }

            return false;
        }
    };
}

char LoopOptimizePass::ID = 0;

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerSkeletonPass(const PassManagerBuilder &,
                            legacy::PassManagerBase &PM) {
    PM.add(new LoopOptimizePass());
}
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                    registerSkeletonPass);
