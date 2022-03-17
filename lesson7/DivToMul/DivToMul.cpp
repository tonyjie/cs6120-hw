#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/IR/IRBuilder.h"
using namespace llvm;

namespace {
    struct DivToMulPass : public FunctionPass {
        static char ID;
        DivToMulPass() : FunctionPass(ID) {}

        virtual bool runOnFunction(Function &F) {

            for (auto& B : F) {
                // errs() << "Basic block (name=" << B.getName() << ") has " << B.size() << " instructions.\n";
                for (auto& I : B) {
                    // errs() << "Opcode: " << I.getOpcode() << "\n" << "OpcodeName: " << I.getOpcodeName() << "\n" << I << "\n";

                    if (I.getOpcodeName() == std::string("sdiv")) { // integer division
                        errs() << "Found Integer Division Instrutcion!\t" << "OpcodeName: " << I.getOpcodeName() << "\n" << I << "\n";
                        
                        auto* pI = &I;

                        IRBuilder<> builder(pI);
                        
                        Value *lhs = pI->getOperand(0);
                        Value *rhs = pI->getOperand(1);
                        // errs() << "lhs: " << *lhs << ";\trhs: " << *rhs << "\n";

                        Value *mul = builder.CreateMul(lhs, rhs); // interger multiplication
                        errs() << "After Transformation: \n" << *mul << "\n"; 

                        for (auto& U : pI->uses()) {
                            User* user = U.getUser();
                            user->setOperand(U.getOperandNo(), mul);
                        }

                    }
                }
            }

        return true;
        }
    };
}

char DivToMulPass::ID = 0;

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerSkeletonPass(const PassManagerBuilder &,
                            legacy::PassManagerBase &PM) {
    PM.add(new DivToMulPass());
}
static RegisterStandardPasses
    RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                    registerSkeletonPass);
